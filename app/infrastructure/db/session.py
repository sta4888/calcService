from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import settings

# Создаём асинхронный движок
engine = create_async_engine(
    settings.database_url,
    echo=True,  # для логов SQL
    future=True,
)

# Создаём асинхронную сессию
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
