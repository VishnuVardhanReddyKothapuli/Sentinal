from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool, create_engine
from app.config import get_settings
from app.models import Base
from app.database import create_database

config = context.config
fileConfig(config.config_file_name)
settings = get_settings()
target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={'paramstyle': 'named'})
    with context.begin_transaction():
        context.run_migrations()
else:
    engine, _ = create_database(settings.database_url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
