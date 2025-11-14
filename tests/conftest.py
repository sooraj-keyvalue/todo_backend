"""
Pytest configuration and fixtures for testing.
Provides database session, test client, and async support.
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.core.database.session import Base, get_db


# Configure pytest-asyncio
def pytest_configure(config: Any) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")


# Test database URL (separate from main database)
TEST_DATABASE_URL = settings.database_url_str.replace("/todo_db", "/todo_db_test")

# Create test engine with proper pool settings for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Track if tables have been created
_tables_created = False


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    This fixture:
    1. Creates tables once (first test only)
    2. Yields a database session for the test
    3. Cleans up all data after the test
    4. Closes the session

    Each test gets a fresh session with clean tables.
    """
    global _tables_created

    # Create tables only once
    if not _tables_created:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True

    # Create a session for the test
    session = TestSessionLocal()
    try:
        yield session
        # Clean up all tables after successful test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with overridden database dependency.

    This fixture:
    1. Overrides the get_db dependency to use the test database
    2. Creates an AsyncClient for making HTTP requests
    3. Yields the client for use in tests

    Usage:
        async def test_endpoint(client: AsyncClient):
            response = await client.get("/api/v1/items")
            assert response.status_code == 200
    """
    from src.main import app

    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio to use asyncio backend."""
    return "asyncio"
