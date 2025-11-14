"""
Base repository with common CRUD operations.
Provides generic repository pattern for all entities.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundException

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository with common CRUD operations.

    Provides standard database operations for any SQLAlchemy model.
    Feature-specific repositories should inherit from this class.

    Type Parameters:
        T: SQLAlchemy model type

    Example:
        ```python
        class UserRepository(BaseRepository[User]):
            async def get_by_email(self, email: str) -> User | None:
                result = await self.db.execute(
                    select(User).filter(User.email == email)
                )
                return result.scalar_one_or_none()
        ```
    """

    def __init__(self, model: type[T], db: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def get(self, id: int) -> T | None:
        """
        Get single entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_or_404(self, id: int) -> T:
        """
        Get entity by ID or raise NotFoundException.

        Args:
            id: Entity ID

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
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, data: dict[str, Any]) -> T:
        """
        Update entity by ID with provided data.

        Only updates fields that exist on the model.
        Ignores fields that don't exist.

        Args:
            id: Entity ID
            data: Dictionary of field names and values to update

        Returns:
            Updated entity

        Raises:
            NotFoundException: If entity not found
        """
        obj = await self.get_or_404(id)

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> None:
        """
        Delete entity by ID.

        Args:
            id: Entity ID

        Raises:
            NotFoundException: If entity not found
        """
        obj = await self.get_or_404(id)
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """
        Count total entities.

        Returns:
            Total count of entities
        """
        result = await self.db.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0

    async def exists(self, id: int) -> bool:
        """
        Check if entity exists by ID.

        Args:
            id: Entity ID

        Returns:
            True if entity exists, False otherwise
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).filter(self.model.id == id)
        )
        count = result.scalar() or 0
        return count > 0
