import hashlib

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, defer

from app.config import settings
from app.database import get_db
from app.models import MediaHistory
from app.schemas import DuplicateMatch, HistoryItem, ModerationResult
from app.services import classifier
from app.services.duplicate_detector import find_duplicate

router = APIRouter(prefix="/api", tags=["moderation"])


@router.post("/moderate", response_model=ModerationResult)
async def moderate(
    file: UploadFile = File(...),
    uploaded_by: str = Form("anonymous"),
    deep_match: bool = Form(False),
    db: Session = Depends(get_db),
) -> ModerationResult:
    """Classify an image/GIF for NSFW content and (optionally) check duplicates."""
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        image = classifier.open_image(raw)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}") from exc

    file_hash = hashlib.sha256(raw).hexdigest()
    media_type = "gif" if (getattr(image, "n_frames", 1) > 1) else "image"

    try:
        nsfw_score, frames_analyzed = classifier.classify_media(image)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=503, detail=f"NSFW model unavailable: {exc}"
        ) from exc

    is_nsfw = nsfw_score >= settings.nsfw_threshold
    nsfw_status = "NSFW" if is_nsfw else "SFW"

    duplicate = DuplicateMatch(is_duplicate=False)
    embedding: list[float] | None = None

    if deep_match:
        try:
            embedding = classifier.generate_embedding(image)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=503, detail=f"Embedding model unavailable: {exc}"
            ) from exc

        existing = db.query(MediaHistory).all()
        duplicate = DuplicateMatch(**find_duplicate(embedding, existing))

    stored = False
    existing_hash = (
        db.query(MediaHistory).filter(MediaHistory.file_hash == file_hash).first()
    )
    if existing_hash is None:
        record = MediaHistory(
            filename=file.filename or "upload",
            file_hash=file_hash,
            media_type=media_type,
            nsfw_status=nsfw_status,
            nsfw_score=nsfw_score,
            is_nsfw=is_nsfw,
            embedding=embedding,
            uploaded_by=uploaded_by or "anonymous",
        )
        db.add(record)
        db.commit()
        stored = True

    return ModerationResult(
        filename=file.filename or "upload",
        file_hash=file_hash,
        media_type=media_type,
        nsfw_status=nsfw_status,
        nsfw_score=round(nsfw_score, 4),
        is_nsfw=is_nsfw,
        frames_analyzed=frames_analyzed,
        duplicate=duplicate,
        stored=stored,
    )

@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = 50, db: Session = Depends(get_db)) -> list[MediaHistory]:
    return (
        db.query(MediaHistory)
        .options(defer(MediaHistory.embedding))
        .order_by(MediaHistory.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
