from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.ENV == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions.
    Handles session cleanup automatically.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# Create sync engine for migrations and testing
sync_engine = create_engine(
    settings.DATABASE_URI.replace("+asyncpg", "+psycopg2"),
    echo=settings.ENV == "development",
    pool_pre_ping=True,
)
