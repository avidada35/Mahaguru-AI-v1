import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.base import Base, create_async_engine, init_models, drop_models
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    """Initialize the database with sample data."""
    logger.info("Dropping all tables...")
    await drop_models()
    
    logger.info("Creating all tables...")
    await init_models()
    
    # Create a test superuser
    async with (await create_async_engine()).begin() as conn:
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.asyncio import AsyncSession
        
        async_session = sessionmaker(conn, expire_on_commit=False, class_=AsyncSession)
        
        async with async_session() as session:
            # Create a test superuser
            test_user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=User.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Admin User",
                is_superuser=True,
            )
            session.add(test_user)
            await session.commit()
            
            logger.info(f"Created superuser with email: {settings.FIRST_SUPERUSER_EMAIL}")
            logger.info(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(init())
