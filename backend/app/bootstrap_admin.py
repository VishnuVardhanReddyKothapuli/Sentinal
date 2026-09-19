"""Explicit local administrator setup; no default or seeded credentials."""
import argparse
import getpass
import os

from sqlalchemy import select

from .config import get_settings
from .database import create_database
from .models import AuditLog, Base, User
from .schemas import Registration
from .security import hasher


def main():
    parser = argparse.ArgumentParser(description='Create a Sentinel administrator')
    parser.add_argument('--username', required=True)
    parser.add_argument('--email', required=True)
    args = parser.parse_args()
    password = os.environ.get('SENTINEL_ADMIN_PASSWORD') or getpass.getpass('New administrator password (12+ characters): ')
    payload = Registration(username=args.username, email=args.email, password=password)
    settings = get_settings()
    engine, sessions = create_database(settings.database_url)
    if settings.auto_create_tables:
        Base.metadata.create_all(engine)
    with sessions() as session:
        if session.scalar(select(User).where((User.username == payload.username) | (User.email == payload.email))):
            raise SystemExit('Username or email already exists; choose a new administrator identity.')
        user = User(username=payload.username, email=payload.email, hashed_password=hasher.hash(payload.password), role='ADMIN')
        session.add(user)
        session.flush()
        session.add(AuditLog(user_id=user.id, action='ADMIN_CREATED', details='Created through local bootstrap command'))
        session.commit()
    engine.dispose()
    print(f'Administrator {payload.username} created.')


if __name__ == '__main__':
    main()
