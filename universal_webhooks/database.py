from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from universal_webhooks.settings import settings

url = make_url(settings.database_url)
if "postgres" in settings.database_url:
    url.set(drivername="postgresql+asyncpg")

engine = create_async_engine(
    settings.database_url.replace("postgres://", "postgresql+asyncpg://")
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()
