from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .models import User

hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)


def get_db(request: Request):
    with request.app.state.session_factory() as session:
        yield session


Db = Annotated[Session, Depends(get_db)]


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def issue_token(user: User, request: Request) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': user.id, 'iat': now, 'exp': now + timedelta(minutes=request.app.state.settings.jwt_expire_minutes), 'iss': 'sentinel', 'aud': 'sentinel-api'}, request.app.state.signing_key, algorithm='HS256')


def current_user(request: Request, db: Db, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> User:
    error = HTTPException(401, 'Valid authentication required', headers={'WWW-Authenticate': 'Bearer'})
    if not credentials:
        raise error
    try:
        claims = jwt.decode(credentials.credentials, request.app.state.signing_key, algorithms=['HS256'], issuer='sentinel', audience='sentinel-api', options={'require': ['sub', 'exp', 'iat']})
        user = db.get(User, claims['sub'])
    except jwt.PyJWTError:
        raise error
    if user is None:
        raise error
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != 'ADMIN':
        raise HTTPException(403, 'Administrator access required')
    return user


AdminUser = Annotated[User, Depends(require_admin)]
