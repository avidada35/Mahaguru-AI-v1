"""Pytest configuration and fixtures for Mahaguru AI backend tests."""
import asyncio
import os
import uuid
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app

# Test database configuration
TEST_DB_NAME = "test_mahaguru"
TEST_DB_USER = "test"
TEST_DB_PASSWORD = "test"

# Override settings for testing
settings.TESTING = True
settings.DATABASE_URL = None  # Will be set by the postgres_container fixture

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def postgres_container():
    """Spin up a Postgres container with pgvector extension."""
    with PostgresContainer(
        "pgvector/pgvector:pg16",
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        dbname=TEST_DB_NAME,
    ) as container:
        # Enable pgvector extension
        container.get_connection_url()
        container.exec(f"psql -U {TEST_DB_USER} -d {TEST_DB_NAME} -c 'CREATE EXTENSION IF NOT EXISTS vector;'")
        
        # Set the DATABASE_URL for the test session
        db_url = container.get_connection_url().replace("postgresql", "postgresql+asyncpg")
        settings.DATABASE_URL = db_url
        
        yield container

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_engine(postgres_container):
    """Create async SQLAlchemy engine with test database."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.SQL_ECHO,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()

@pytest_asyncio.fixture
def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test case."""
    connection = await async_engine.connect()
    transaction = await connection.begin()
    session_maker = sessionmaker(
        connection, expire_on_commit=False, class_=AsyncSession
    )
    session = session_maker()
    
    # Override the get_db dependency
    async def override_get_db():
        try:
            yield session
        finally:
            await session.close()
    
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Clean up
    await session.close()
    await transaction.rollback()
    await connection.close()
    fastapi_app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_user_data():
    """Test user data for creating test users."""
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }

@pytest.fixture
def test_document_data():
    """Test document data for creating test documents."""
    return {
        "title": "Test Document",
        "description": "A test document",
        "file_path": str(TEST_DATA_DIR / "test_document.txt"),
    }

@pytest.fixture
def test_queries():
    """Sample test queries for retrieval evaluation."""
    return [
        {"query": "What is Mahaguru AI?", "relevant_ids": [1, 2]},
        {"query": "How to use the API?", "relevant_ids": [3, 4]},
    ]

# Ensure test data directory exists
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create a sample test document if it doesn't exist
TEST_DOC_PATH = TEST_DATA_DIR / "test_document.txt"
if not TEST_DOC_PATH.exists():
    TEST_DOC_PATH.write_text(
        "Mahaguru AI is an intelligent document processing platform.\n"
        "It helps users extract insights from their documents using AI."
    )
