import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.core.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


# Подставляем в конфиг Alembic
config.set_main_option("sqlalchemy.url", settings.alembic_database_url)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# импортируем модели для автогенерации
from app.infrastructure.db.models import Base  # noqa

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    async_engine = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        future=True
    )

    async def do_run_migrations():
        async with async_engine.begin() as conn:
            # run_sync передаст синхронный контекст Alembic
            await conn.run_sync(lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            ) or context.run_migrations())

    import asyncio
    asyncio.run(do_run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()