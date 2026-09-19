from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


def create_database(url: str):
    is_sqlite = url.startswith('sqlite')
    if is_sqlite:
        database = make_url(url).database
        if database and database != ':memory:':
            Path(database).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, connect_args={'check_same_thread': False} if is_sqlite else {}, pool_pre_ping=True)
    if is_sqlite:
        @event.listens_for(engine, 'connect')
        def sqlite_options(connection, _):
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.execute('PRAGMA busy_timeout=5000')
            cursor.close()
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
