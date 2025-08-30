from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.db.session import sync_engine

# Import all models here to ensure they are registered with SQLAlchemy
from app.models import document, document_chunk, user  # noqa: F401

Base = declarative_base()


def create_tables() -> None:
    """
    Create all database tables.
    
    Note: In production, use migrations instead of this function.
    This is only for development and testing.
    """
    Base.metadata.create_all(bind=sync_engine)


async def create_async_engine() -> AsyncEngine:
    """Create and return an async SQLAlchemy engine."""
    from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
    
    engine = _create_async_engine(
        settings.DATABASE_URI,
        echo=settings.ENV == "development",
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    
    return engine


async def init_models() -> None:
    """Initialize database models (create tables)."""
    async with (await create_async_engine()).begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_models() -> None:
    """Drop all database tables."""
    async with (await create_async_engine()).begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Import all models to ensure they're registered with SQLAlchemy
# This must be after Base is defined
from app.models.document import Document  # noqa: F401, E402
from app.models.document_chunk import DocumentChunk  # noqa: F401, E402
from app.models.user import User  # noqa: F401, E402
