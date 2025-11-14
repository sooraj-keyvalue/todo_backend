"""
Base repository with common CRUD operations.
Provides generic repository pattern for all entities.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundException

T = TypeVar("T")
ID = TypeVar("ID", int, UUID)  # Support both int and UUID IDs


class BaseRepository(Generic[T, ID]):
    """
    Base repository with common CRUD operations.

    Provides standard database operations for any SQLAlchemy model.
    Feature-specific repositories should inherit from this class.

    Type Parameters:
        T: SQLAlchemy model type
        ID: Primary key type (int or UUID)

    Example:
        ```python
        # With UUID IDs
        class UserRepository(BaseRepository[User, UUID]):
            async def get_by_email(self, email: str) -> User | None:
                result = await self.db.execute(
                    select(User).filter(User.email == email)
                )
                return result.scalar_one_or_none()

        # With int IDs
        class LegacyRepository(BaseRepository[Legacy, int]):
            pass
        ```

    Transaction Management:
        By default, create/update/delete operations auto-commit.
        To manage transactions manually, set auto_commit=False and
        handle commits in your service layer.
    """

    def __init__(
        self, model: type[T], db: AsyncSession, auto_commit: bool = True
    ) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Async database session
            auto_commit: Whether to auto-commit after write operations.
                        Set to False for manual transaction management.
        """
        self.model = model
        self.db = db
        self.auto_commit = auto_commit

    async def get(self, id: ID) -> T | None:
        """
        Get single entity by ID.

        Args:
            id: Entity ID (int or UUID)

        Returns:
            Entity if found, None otherwise
        """
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_or_404(self, id: ID) -> T:
        """
        Get entity by ID or raise NotFoundException.

        Args:
            id: Entity ID (int or UUID)

        Returns:
            Entity

        Raises:
            NotFoundException: If entity not found
        """
        obj = await self.get(id)
        if not obj:
            raise NotFoundException(
                message=f"{self.model.__name__} with id {id} not found",
                code=f"{self.model.__name__.upper()}_NOT_FOUND",
            )
        return obj

    async def create(self, obj: T) -> T:
        """
        Create new entity.

        Args:
            obj: Entity instance to create

        Returns:
            Created entity with ID and generated fields populated

        Note:
            Auto-commits if auto_commit=True (default).
            Otherwise, you must commit manually in your service layer.
        """
        self.db.add(obj)
        if self.auto_commit:
            await self.db.commit()
            await self.db.refresh(obj)
        else:
            await self.db.flush()  # Get ID without committing
            await self.db.refresh(obj)
        return obj

    async def update(self, id: ID, data: dict[str, Any]) -> T:
        """
        Update entity by ID with provided data.

        Only updates fields that exist on the model.
        Ignores fields that don't exist.

        Args:
            id: Entity ID (int or UUID)
            data: Dictionary of field names and values to update

        Returns:
            Updated entity

        Raises:
            NotFoundException: If entity not found

        Note:
            Auto-commits if auto_commit=True (default).
            Otherwise, you must commit manually in your service layer.
        """
        obj = await self.get_or_404(id)

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        if self.auto_commit:
            await self.db.commit()
            await self.db.refresh(obj)
        else:
            await self.db.flush()
            await self.db.refresh(obj)
        return obj

    async def delete(self, id: ID) -> None:
        """
        Delete entity by ID.

        Args:
            id: Entity ID (int or UUID)

        Raises:
            NotFoundException: If entity not found

        Note:
            Auto-commits if auto_commit=True (default).
            Otherwise, you must commit manually in your service layer.
        """
        obj = await self.get_or_404(id)
        await self.db.delete(obj)
        if self.auto_commit:
            await self.db.commit()

    async def count(self) -> int:
        """
        Count total entities.

        Returns:
            Total count of entities
        """
        result = await self.db.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0

    async def exists(self, id: ID) -> bool:
        """
        Check if entity exists by ID.

        Args:
            id: Entity ID (int or UUID)

        Returns:
            True if entity exists, False otherwise
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).filter(self.model.id == id)
        )
        count = result.scalar() or 0
        return count > 0
