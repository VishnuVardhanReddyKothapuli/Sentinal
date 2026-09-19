import asyncio
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from .config import Settings, get_settings
from .database import create_database
from .media import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, save_upload, validate_media
from .models import AnalysisRecord, AuditLog, Base, User
from .schemas import Login, PurgeRequest, Registration
from .security import AdminUser, CurrentUser, Db, hasher, issue_token, verify_password

logger = logging.getLogger('sentinel')


async def run_analysis(path: Path, mode: str, user_id: str, record_id: str) -> dict:
    from ai_engine.pipeline import analyze_media
    return await analyze_media(path, mode, user_id, record_id)


def capabilities() -> dict:
    from ai_engine.pipeline import get_capabilities
    return get_capabilities()


async def remove_vector(record_id: str, user_id: str) -> None:
    from ai_engine.pipeline import delete_record
    await delete_record(record_id, user_id)


def user_json(user: User) -> dict:
    return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}


def record_json(record: AnalysisRecord) -> dict:
    return {**record.result, 'id': record.id, 'file_name': record.file_name,
            'file_type': record.file_type, 'file_url': record.file_url,
            'analysis_type': record.analysis_type, 'overall_status': record.overall_status,
            'created_at': record.created_at.isoformat() + ('Z' if record.created_at.tzinfo is None else '')}


def metrics(db) -> dict:
    return {'total_scans': db.scalar(select(func.count()).select_from(AnalysisRecord)) or 0,
            'flagged_count': db.scalar(select(func.count()).select_from(AnalysisRecord).where(AnalysisRecord.overall_status == 'FLAGGED')) or 0,
            'registered_users': db.scalar(select(func.count()).select_from(User)) or 0}


def owned_record(db, record_id: str, user: User) -> AnalysisRecord:
    record = db.get(AnalysisRecord, record_id)
    if record is None or (record.user_id != user.id and user.role != 'ADMIN'):
        raise HTTPException(404, 'Analysis record not found')
    return record


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    uploads = (settings.upload_dir or settings.data_dir / 'uploads').resolve()
    engine, sessions = create_database(settings.database_url)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        uploads.mkdir(parents=True, exist_ok=True)
        application.state.signing_key = settings.signing_key()
        if settings.auto_create_tables:
            Base.metadata.create_all(engine)
        yield
        engine.dispose()

    application = FastAPI(title='Sentinel API', version='1.0.0', lifespan=lifespan)
    application.state.settings = settings
    application.state.session_factory = sessions
    application.state.engine = engine
    application.state.inference_semaphore = asyncio.Semaphore(max(1, settings.inference_concurrency))
    application.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()], allow_credentials=False, allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Authorization', 'Content-Type'])

    @application.middleware('http')
    async def headers(request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        if request.url.path.startswith('/api/v1/') and request.url.path != '/api/v1/metrics/public':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @application.get('/api/v1/health')
    def health(db: Db):
        db.execute(select(1))
        return {'status': 'ok', 'database': 'connected', 'capabilities': capabilities()}

    @application.post('/api/v1/auth/register', status_code=201)
    def register(payload: Registration, request: Request, db: Db):
        user = User(username=payload.username, email=payload.email, hashed_password=hasher.hash(payload.password), role='USER')
        db.add(user)
        try:
            db.flush()
            db.add(AuditLog(user_id=user.id, action='ACCOUNT_CREATED', details='User registered'))
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, 'Username or email already registered')
        return {'access_token': issue_token(user, request), 'token_type': 'bearer', 'user': user_json(user)}

    @application.post('/api/v1/auth/login')
    def login(payload: Login, request: Request, db: Db):
        identity = payload.username.lower().strip()
        user = db.scalar(select(User).where(or_(User.username == identity, User.email == identity)))
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(401, 'Invalid username or password', headers={'WWW-Authenticate': 'Bearer'})
        db.add(AuditLog(user_id=user.id, action='LOGIN', details='Successful authentication'))
        db.commit()
        return {'access_token': issue_token(user, request), 'token_type': 'bearer', 'user': user_json(user)}

    @application.get('/api/v1/auth/me')
    def me(user: CurrentUser):
        return user_json(user)

    @application.get('/api/v1/metrics/public')
    def public_metrics(db: Db):
        return metrics(db)

    @application.post('/api/v1/analyze/{mode}', status_code=201)
    async def analyze(mode: str, request: Request, db: Db, user: CurrentUser, file: UploadFile = File(...)):
        if mode not in {'nsfw', 'similarity', 'combined'}:
            raise HTTPException(404, 'Unknown analysis mode')
        file_name = (file.filename or 'upload').replace('\\', '/').rsplit('/', 1)[-1][:255]
        extension = Path(file_name).suffix.lower()
        if extension not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            await file.close()
            raise HTTPException(415, 'Unsupported media extension')
        record_id = str(uuid4())
        path = uploads / f'{record_id}{extension}'
        analysis_started = False
        persisted = False
        try:
            await save_upload(file, path, settings.max_upload_mb * 1024 * 1024)
            file_type = await run_in_threadpool(validate_media, path)
            async with request.app.state.inference_semaphore:
                analysis_started = True
                result = await run_in_threadpool(lambda: asyncio.run(run_analysis(path, mode, user.id, record_id)))
            # Missing inference can never be mistaken for a successful safety verdict.
            result.setdefault('overall_status', 'REVIEW')
            result.setdefault('warnings', [])
            result.setdefault('scores', None)
            result.setdefault('matches', [])
            result.setdefault('capabilities', {})
            result.setdefault('extracted_text', '')
            result.setdefault('text_flagged', False)
            result.setdefault('text_flag_reason', None)
            result.setdefault('ai_explanation', None)
            result.setdefault('similarity_score', None)
            result.setdefault('is_duplicate', False)
            result.setdefault('frames_analyzed', 1 if file_type == 'IMAGE' else 0)
            if result['overall_status'] not in {'SAFE', 'FLAGGED', 'REVIEW'}:
                result['overall_status'] = 'REVIEW'
            # Filter stale and foreign vectors again at the database boundary.
            raw_matches = result['matches']
            visible_matches = []
            for match in raw_matches:
                match_id = match.get('record_id') or match.get('id')
                matched = db.get(AnalysisRecord, match_id) if match_id else None
                if matched and matched.user_id == user.id:
                    visible_matches.append({**match, 'record_id': matched.id, 'file_name': matched.file_name, 'file_type': matched.file_type, 'file_url': matched.file_url})
            result['matches'] = visible_matches
            if len(visible_matches) != len(raw_matches):
                result['overall_status'] = 'REVIEW' if result['overall_status'] != 'FLAGGED' else 'FLAGGED'
                result['warnings'].append('Some similarity references are no longer available; review retained matches.')
                result['similarity_score'] = max((match.get('similarity_score', match.get('score', 0)) for match in visible_matches), default=None)
                result['is_duplicate'] = (result['similarity_score'] or 0) >= 88
            elif not visible_matches:
                result['is_duplicate'] = False
                result['similarity_score'] = 0.0 if result.get('checks_complete', {}).get('similarity') else None
            scores = result.get('scores') or {}
            record = AnalysisRecord(id=record_id, user_id=user.id, file_name=file_name, file_type=file_type,
                file_url=f'/api/v1/media/{record_id}', storage_path=str(path), analysis_type=mode.upper(),
                score_safe=scores.get('safe'), score_explicit=scores.get('explicit'), score_suggestive=scores.get('suggestive'), score_gore=scores.get('gore'),
                extracted_text=result.get('extracted_text'), text_flagged=result.get('text_flagged', False), text_flag_reason=(result.get('text_flag_reason') or '')[:255] or None,
                vector_id=result.get('vector_id'), is_duplicate=result.get('is_duplicate', False), matched_record_id=visible_matches[0]['record_id'] if visible_matches else None,
                similarity_score=result.get('similarity_score'), ai_explanation=result.get('ai_explanation'), overall_status=result['overall_status'], result=result)
            db.add(record)
            db.add(AuditLog(user_id=user.id, action='ANALYSIS_COMPLETED', details=f'{mode.upper()} {record_id}: {record.overall_status}'))
            db.commit()
            persisted = True
            return record_json(record)
        except HTTPException:
            raise
        except ValueError as exc:
            logger.warning('Media decoding failed for record %s', record_id)
            raise HTTPException(422, 'Media could not be analyzed; check that the file is valid') from exc
        except Exception as exc:
            logger.exception('Analysis failed for record %s', record_id)
            raise HTTPException(503, 'Analysis service is temporarily unavailable; please retry') from exc
        finally:
            if not persisted:
                db.rollback()
                path.unlink(missing_ok=True)
                if analysis_started:
                    try:
                        await remove_vector(record_id, user.id)
                    except Exception:
                        logger.exception('Vector cleanup failed for %s', record_id)

    @application.get('/api/v1/user/history')
    def history(db: Db, user: CurrentUser, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), status: str | None = None, search: str = Query('', max_length=255)):
        query = select(AnalysisRecord).where(AnalysisRecord.user_id == user.id)
        if status:
            if status.upper() not in {'SAFE', 'FLAGGED', 'REVIEW'}:
                raise HTTPException(422, 'Unknown status filter')
            query = query.where(AnalysisRecord.overall_status == status.upper())
        if search:
            query = query.where(AnalysisRecord.file_name.contains(search, autoescape=True))
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        records = db.scalars(query.order_by(AnalysisRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
        return {'items': [record_json(record) for record in records], 'total': total, 'page': page, 'page_size': page_size}

    @application.get('/api/v1/user/history/{record_id}')
    def detail(record_id: str, db: Db, user: CurrentUser):
        return record_json(owned_record(db, record_id, user))

    @application.get('/api/v1/media/{record_id}')
    def media(record_id: str, db: Db, user: CurrentUser):
        record = owned_record(db, record_id, user)
        path = Path(record.storage_path).resolve()
        if not path.is_relative_to(uploads) or not path.is_file():
            raise HTTPException(404, 'Media file not found')
        return FileResponse(path, filename=record.file_name, content_disposition_type='inline')

    async def delete_records(db, records: list[AnalysisRecord], actor: User):
        for record in records:
            if not record.vector_id:
                continue
            try:
                await remove_vector(record.id, record.user_id)
            except Exception as exc:
                logger.exception('Vector deletion failed for %s', record.id)
                raise HTTPException(503, 'Vector service unavailable; deletion was not completed') from exc
        for record in records:
            path = Path(record.storage_path).resolve()
            if path.is_relative_to(uploads):
                path.unlink(missing_ok=True)
            db.delete(record)
            db.add(AuditLog(user_id=actor.id, action='RECORD_DELETED', details=record.id))
        db.commit()
        return {'deleted': len(records)}

    @application.delete('/api/v1/user/history/{record_id}')
    async def delete_own(record_id: str, db: Db, user: CurrentUser):
        return await delete_records(db, [owned_record(db, record_id, user)], user)

    @application.get('/api/v1/admin/overview')
    def overview(db: Db, user: AdminUser):
        records = db.scalars(select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(100)).all()
        users = {item.id: item.username for item in db.scalars(select(User)).all()}
        logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)).all()
        return {**metrics(db), 'records': [{**record_json(record), 'user_id': record.user_id, 'username': users.get(record.user_id, 'Unknown')} for record in records],
                'logs': [{'id': log.id, 'user_id': log.user_id, 'action': log.action, 'details': log.details, 'created_at': log.created_at.isoformat()} for log in logs]}

    @application.delete('/api/v1/admin/records/{record_id}')
    async def delete_any(record_id: str, db: Db, user: AdminUser):
        return await delete_records(db, [owned_record(db, record_id, user)], user)

    @application.post('/api/v1/admin/purge')
    async def purge(payload: PurgeRequest, db: Db, user: AdminUser):
        records = db.scalars(select(AnalysisRecord).where(AnalysisRecord.id.in_(set(payload.ids)))).all()
        return await delete_records(db, records, user)

    return application


app = create_app()
