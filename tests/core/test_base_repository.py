"""
Tests for BaseRepository.
Verifies all CRUD operations with a mock model.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.base_repository import BaseRepository
from src.core.database.session import Base
from src.core.exceptions import NotFoundException


# Mock model for testing
class TestModel(Base):
    """Test model for repository testing."""

    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


@pytest_asyncio.fixture
async def test_repo(db_session: AsyncSession) -> BaseRepository[TestModel, int]:
    """Create a test repository instance with auto-commit enabled."""
    return BaseRepository(TestModel, db_session, auto_commit=True)


@pytest_asyncio.fixture
async def test_repo_no_commit(
    db_session: AsyncSession,
) -> BaseRepository[TestModel, int]:
    """Create a test repository instance with auto-commit disabled."""
    return BaseRepository(TestModel, db_session, auto_commit=False)


@pytest.mark.asyncio
async def test_create(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test creating a new entity."""
    obj = TestModel(name="Test Item", description="Test description")
    created = await test_repo.create(obj)

    assert created.id is not None
    assert created.name == "Test Item"
    assert created.description == "Test description"
    assert created.created_at is not None


@pytest.mark.asyncio
async def test_get_existing(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test getting an existing entity by ID."""
    # Create test data
    obj = TestModel(name="Test Item")
    created = await test_repo.create(obj)

    # Get by ID
    result = await test_repo.get(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.name == "Test Item"


@pytest.mark.asyncio
async def test_get_nonexistent(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test getting a nonexistent entity returns None."""
    result = await test_repo.get(99999)
    assert result is None


@pytest.mark.asyncio
async def test_get_or_404_existing(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test get_or_404 with existing entity."""
    obj = TestModel(name="Test Item")
    created = await test_repo.create(obj)

    result = await test_repo.get_or_404(created.id)

    assert result is not None
    assert result.id == created.id


@pytest.mark.asyncio
async def test_get_or_404_nonexistent(
    test_repo: BaseRepository[TestModel, int],
) -> None:
    """Test get_or_404 raises NotFoundException for nonexistent entity."""
    with pytest.raises(NotFoundException) as exc_info:
        await test_repo.get_or_404(99999)

    assert "TestModel" in str(exc_info.value)
    assert "99999" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test updating an entity."""
    # Create test data
    obj = TestModel(name="Original Name", description="Original description")
    created = await test_repo.create(obj)

    # Update
    update_data = {"name": "Updated Name", "description": "Updated description"}
    updated = await test_repo.update(created.id, update_data)

    assert updated.id == created.id
    assert updated.name == "Updated Name"
    assert updated.description == "Updated description"


@pytest.mark.asyncio
async def test_update_partial(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test partial update (only some fields)."""
    obj = TestModel(name="Original Name", description="Original description")
    created = await test_repo.create(obj)

    # Update only name
    update_data = {"name": "Updated Name"}
    updated = await test_repo.update(created.id, update_data)

    assert updated.name == "Updated Name"
    assert updated.description == "Original description"  # Unchanged


@pytest.mark.asyncio
async def test_update_nonexistent(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test updating a nonexistent entity raises NotFoundException."""
    with pytest.raises(NotFoundException):
        await test_repo.update(99999, {"name": "Updated"})


@pytest.mark.asyncio
async def test_update_ignores_invalid_fields(
    test_repo: BaseRepository[TestModel, int],
) -> None:
    """Test that update ignores fields that don't exist on the model."""
    obj = TestModel(name="Original Name")
    created = await test_repo.create(obj)

    # Try to update with invalid field
    update_data = {"name": "Updated Name", "invalid_field": "should be ignored"}
    updated = await test_repo.update(created.id, update_data)

    assert updated.name == "Updated Name"
    assert not hasattr(updated, "invalid_field")


@pytest.mark.asyncio
async def test_delete(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test deleting an entity."""
    obj = TestModel(name="To Delete")
    created = await test_repo.create(obj)

    # Delete
    await test_repo.delete(created.id)

    # Verify deleted
    result = await test_repo.get(created.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_nonexistent(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test deleting a nonexistent entity raises NotFoundException."""
    with pytest.raises(NotFoundException):
        await test_repo.delete(99999)


@pytest.mark.asyncio
async def test_count_empty(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test counting with no entities."""
    count = await test_repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_count_with_entities(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test counting entities."""
    # Create multiple entities
    await test_repo.create(TestModel(name="Item 1"))
    await test_repo.create(TestModel(name="Item 2"))
    await test_repo.create(TestModel(name="Item 3"))

    count = await test_repo.count()
    assert count == 3


@pytest.mark.asyncio
async def test_exists_true(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test exists returns True for existing entity."""
    obj = TestModel(name="Test Item")
    created = await test_repo.create(obj)

    exists = await test_repo.exists(created.id)
    assert exists is True


@pytest.mark.asyncio
async def test_exists_false(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test exists returns False for nonexistent entity."""
    exists = await test_repo.exists(99999)
    assert exists is False


@pytest.mark.asyncio
async def test_multiple_operations(test_repo: BaseRepository[TestModel, int]) -> None:
    """Test multiple operations in sequence."""
    # Create
    obj1 = await test_repo.create(TestModel(name="Item 1"))
    obj2 = await test_repo.create(TestModel(name="Item 2"))

    # Count
    assert await test_repo.count() == 2

    # Update
    await test_repo.update(obj1.id, {"name": "Updated Item 1"})

    # Get
    updated = await test_repo.get(obj1.id)
    assert updated.name == "Updated Item 1"

    # Delete
    await test_repo.delete(obj2.id)

    # Verify
    assert await test_repo.count() == 1
    assert await test_repo.exists(obj1.id) is True
    assert await test_repo.exists(obj2.id) is False


@pytest.mark.asyncio
async def test_manual_transaction_create(
    test_repo_no_commit: BaseRepository[TestModel, int], db_session: AsyncSession
) -> None:
    """Test create with manual transaction management."""
    obj = TestModel(name="Manual Transaction Item")
    created = await test_repo_no_commit.create(obj)

    # Object should have ID from flush
    assert created.id is not None
    assert created.name == "Manual Transaction Item"

    # But not committed yet - manually commit
    await db_session.commit()

    # Verify it's persisted
    result = await test_repo_no_commit.get(created.id)
    assert result is not None
    assert result.name == "Manual Transaction Item"


@pytest.mark.asyncio
async def test_manual_transaction_rollback(
    test_repo_no_commit: BaseRepository[TestModel, int], db_session: AsyncSession
) -> None:
    """Test rollback with manual transaction management."""
    obj = TestModel(name="To Rollback")
    created = await test_repo_no_commit.create(obj)

    # Object has ID but not committed
    assert created.id is not None

    # Rollback instead of commit
    await db_session.rollback()

    # Verify it's not persisted
    result = await test_repo_no_commit.get(created.id)
    assert result is None


@pytest.mark.asyncio
async def test_manual_transaction_multiple_operations(
    test_repo_no_commit: BaseRepository[TestModel, int], db_session: AsyncSession
) -> None:
    """Test multiple operations in a single transaction."""
    # Create multiple items without committing
    obj1 = await test_repo_no_commit.create(TestModel(name="Item 1"))
    obj2 = await test_repo_no_commit.create(TestModel(name="Item 2"))
    obj3 = await test_repo_no_commit.create(TestModel(name="Item 3"))

    # Update one
    await test_repo_no_commit.update(obj1.id, {"name": "Updated Item 1"})

    # Delete one
    await test_repo_no_commit.delete(obj3.id)

    # Now commit all at once
    await db_session.commit()

    # Verify final state
    assert await test_repo_no_commit.count() == 2
    result1 = await test_repo_no_commit.get(obj1.id)
    assert result1.name == "Updated Item 1"
    assert await test_repo_no_commit.exists(obj2.id) is True
    assert await test_repo_no_commit.exists(obj3.id) is False
