# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based todo backend API built with FastAPI and PostgreSQL, following Test-Driven Development (TDD) practices.

**Tech Stack:**
- Python 3.12.11+
- FastAPI - Web framework
- PostgreSQL - Database
- SQLAlchemy - ORM (async)
- Alembic - Database migrations
- `uv` - Package management
- pytest - Testing framework
- ruff - Linting and formatting
- mypy - Type checking

## Development Commands

**Install dependencies:**
```bash
uv sync
```

**Run the application:**
```bash
uvicorn src.main:app --reload
```

**Run tests:**
```bash
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=src --cov-report=term-missing
```

**Run linter:**
```bash
ruff check .
```

**Format code:**
```bash
ruff format .
```

**Type checking:**
```bash
mypy src
```

**Database migrations:**
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Architecture

### Hybrid Vertical Slice Pattern

The project follows a hybrid vertical slice architecture:

```text
src/
├── main.py                         # FastAPI application entry point
├── core/                           # Core infrastructure (can't run without these)
│   ├── config.py                   # Application configuration
│   ├── database/
│   │   ├── session.py              # DB connection/pooling
│   │   ├── base_repository.py     # Generic repository with common CRUD
│   │   ├── query_helper.py        # Helper for filtering, sorting, pagination
│   │   └── pagination.py          # Pagination utilities
│   ├── middleware/
│   │   ├── request_tracking.py    # Request ID and tracking
│   │   └── error_handling.py      # Centralized error handling
│   ├── exceptions.py               # Common exception classes
│   └── dependencies.py             # FastAPI dependency injection
├── shared/                         # Shared utilities (extracted when 3+ features need it)
│   ├── enums.py                    # Infrastructure-level enums only
│   ├── constants.py                # Application-wide constants
│   └── utils.py                    # Utility functions
├── features/                       # Feature-specific vertical slices
│   └── todos/                      # Example feature
│       ├── api.py                  # FastAPI endpoints
│       ├── schemas.py              # Pydantic models (request/response)
│       ├── models.py               # SQLAlchemy models (database)
│       ├── service.py              # Business logic
│       ├── repository.py           # Data access (uses BaseRepository + QueryHelper)
│       ├── exceptions.py           # Feature-specific exceptions
│       └── tests/                  # Tests alongside the feature
│           ├── test_api.py
│           ├── test_service.py
│           └── test_repository.py
└── tests/
    └── core/                       # Tests for core infrastructure only
        └── test_database.py
```

**Key architectural components:**

- **Core directory**: Essential infrastructure - database, middleware, config, exceptions. Cannot run without these.
- **Shared directory**: Utilities and helpers extracted when 3+ features need them. Keep minimal.
- **Features directory**: Each feature is self-contained with its own models, routes, services, tests, and repositories.
- **BaseRepository**: Generic repository pattern providing common CRUD operations via inheritance.
- **QueryHelper**: Composition-based helper for dynamic filtering, sorting, and pagination from API query params.

## Development Rules

### Test-Driven Development (TDD)

**ALWAYS write tests before implementing functionality:**
1. Write failing test first
2. Implement minimum code to pass the test
3. Refactor while keeping tests green
4. All new features require corresponding tests

### Code Style

**Type hints are mandatory:**
- All function parameters must have type hints
- All function return types must be specified
- Use `typing` module types where appropriate

**Naming conventions:**
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**Formatting:**
- Use `ruff` for linting and formatting
- Line length: 100 characters
- Use double quotes for strings
- Follow PEP 8 standards

### API Design

**REST conventions:**
- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Use plural nouns for resource endpoints (`/todos`, not `/todo`)
- Return appropriate HTTP status codes
- Use path parameters for IDs: `/todos/{todo_id}`
- Use query parameters for filtering, sorting, pagination

**Response format:**

All API responses MUST use the `APIResponse` wrapper for consistency.

**Response Schema** (`core/schemas.py`):

```python
from typing import TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class ResponseMetadata(BaseModel):
    """Metadata included in all API responses"""
    request_id: str = Field(..., description="Unique request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    path: str = Field(..., description="Request path")
    method: str = Field(..., description="HTTP method")

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    data: T = Field(..., description="Response data")
    meta: ResponseMetadata = Field(..., description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {"id": 1, "title": "Example"},
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "path": "/api/todos/1",
                    "method": "GET"
                }
            }
        }

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional error details")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail
    meta: ResponseMetadata
```

**Usage in Routes:**

```python
from core.schemas import APIResponse, ResponseMetadata
from fastapi import Request

@router.get("/{todo_id}", response_model=APIResponse[TodoResponse])
async def get_todo(
    request: Request,
    todo_id: int,
    service: TodoServiceDep,
) -> APIResponse[TodoResponse]:
    """Get a single todo by ID"""
    todo = await service.get_todo(todo_id)

    # Meta is automatically added by response middleware
    return APIResponse(data=todo)
```

**Error handling:**

All errors must be caught by the central error handling middleware and return a consistent format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Todo with id 123 not found",
    "details": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/todos/123",
    "method": "GET"
  }
}
```

### Middleware Requirements

**Request Tracking Middleware** (`core/middleware/request_tracking.py`):

```python
import uuid
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Add request tracking to all requests"""

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store in request state for access in routes
        request.state.request_id = request_id
        request.state.timestamp = datetime.utcnow()
        request.state.path = request.url.path
        request.state.method = request.method

        # Add to response headers
        response: Response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
```

**Error Handling Middleware** (`core/middleware/error_handling.py`):

```python
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError
from core.exceptions import (
    NotFoundException,
    ValidationException,
    AuthorizationException,
)
from core.schemas import ErrorResponse, ErrorDetail, ResponseMetadata

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Centralized error handling for all exceptions"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle exceptions and return consistent error response"""

        # Get request tracking info
        request_id = getattr(request.state, "request_id", "unknown")
        timestamp = getattr(request.state, "timestamp", datetime.utcnow())
        path = request.url.path
        method = request.method

        # Create metadata
        meta = ResponseMetadata(
            request_id=request_id,
            timestamp=timestamp,
            path=path,
            method=method
        )

        # Handle specific exception types
        if isinstance(exc, NotFoundException):
            error_detail = ErrorDetail(
                code="NOT_FOUND",
                message=str(exc),
                details=None
            )
            status_code = status.HTTP_404_NOT_FOUND

        elif isinstance(exc, ValidationException):
            error_detail = ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(exc),
                details=getattr(exc, "details", None)
            )
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        elif isinstance(exc, AuthorizationException):
            error_detail = ErrorDetail(
                code="FORBIDDEN",
                message=str(exc),
                details=None
            )
            status_code = status.HTTP_403_FORBIDDEN

        elif isinstance(exc, IntegrityError):
            # Database integrity errors (unique constraints, etc.)
            logger.error(f"Database integrity error: {exc}", exc_info=True)
            error_detail = ErrorDetail(
                code="INTEGRITY_ERROR",
                message="A database constraint was violated",
                details=None  # Don't expose internal DB details
            )
            status_code = status.HTTP_409_CONFLICT

        else:
            # Unexpected errors
            logger.error(
                f"Unexpected error: {exc}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method
                }
            )
            error_detail = ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                details=None  # Never expose internal error details
            )
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        # Build error response
        error_response = ErrorResponse(error=error_detail, meta=meta)

        return JSONResponse(
            status_code=status_code,
            content=error_response.model_dump()
        )
```

**Exception Classes** (`core/exceptions.py`):

```python
class BaseAPIException(Exception):
    """Base exception for all API exceptions"""
    pass

class NotFoundException(BaseAPIException):
    """Raised when a resource is not found"""
    pass

class ValidationException(BaseAPIException):
    """Raised when validation fails"""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details

class AuthorizationException(BaseAPIException):
    """Raised when user is not authorized"""
    pass

class AuthenticationException(BaseAPIException):
    """Raised when authentication fails"""
    pass
```

**Middleware Registration** (`src/main.py`):

```python
from fastapi import FastAPI
from core.middleware.request_tracking import RequestTrackingMiddleware
from core.middleware.error_handling import ErrorHandlingMiddleware

app = FastAPI(title="Todo API")

# Add middleware (order matters - first added = outermost)
app.add_middleware(ErrorHandlingMiddleware)  # Catches all errors
app.add_middleware(RequestTrackingMiddleware)  # Tracks all requests

# Register routers
from features.todos.api import router as todos_router
app.include_router(todos_router, prefix="/api")
```

**Middleware Rules:**

- Request tracking middleware MUST be added to capture request metadata
- Error handling middleware MUST wrap all routes to catch exceptions
- Never expose internal error details (stack traces, DB errors) to clients
- Always log errors with request context for debugging
- Return consistent error response format using `ErrorResponse` schema

### Database

**Repository Pattern - BaseRepository + QueryHelper:**

The project uses a combination of:

1. **BaseRepository (Inheritance)** - Provides common CRUD operations for all entities
2. **QueryHelper (Composition)** - Standardizes dynamic filtering, sorting, and pagination

**BaseRepository** (`core/database/base_repository.py`):

```python
from typing import Generic, TypeVar, Type, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from core.exceptions import NotFoundException

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[T]:
        """Get single entity by ID"""
        result = await self.db.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_or_404(self, id: int) -> T:
        """Get entity by ID or raise NotFoundException"""
        obj = await self.get(id)
        if not obj:
            raise NotFoundException(f"{self.model.__name__} with id {id} not found")
        return obj

    async def create(self, obj: T) -> T:
        """Create new entity"""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, data: dict[str, Any]) -> T:
        """Update entity by ID with provided data"""
        obj = await self.get_or_404(id)

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> None:
        """Delete entity by ID"""
        obj = await self.get_or_404(id)
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """Count total entities"""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar()

    async def exists(self, id: int) -> bool:
        """Check if entity exists by ID"""
        result = await self.db.execute(
            select(func.count()).select_from(self.model).filter(self.model.id == id)
        )
        return result.scalar() > 0
```

**QueryHelper** (`core/database/query_helper.py`):

```python
from typing import Type, Any
from sqlalchemy import Select

class QueryHelper:
    """Helper for building dynamic queries from API query params"""

    # Supported filter operations
    ALLOWED_OPERATIONS = {
        'eq': lambda col, val: col == val,           # Equal
        'ne': lambda col, val: col != val,           # Not equal
        'gt': lambda col, val: col > val,            # Greater than
        'gte': lambda col, val: col >= val,          # Greater than or equal
        'lt': lambda col, val: col < val,            # Less than
        'lte': lambda col, val: col <= val,          # Less than or equal
        'like': lambda col, val: col.like(f"%{val}%"),  # Case-sensitive LIKE
        'ilike': lambda col, val: col.ilike(f"%{val}%"), # Case-insensitive LIKE
        'in': lambda col, val: col.in_(val),         # IN list
        'not_in': lambda col, val: col.not_in(val),  # NOT IN list
        'is_null': lambda col, val: col.is_(None) if val else col.is_not(None),
    }

    @staticmethod
    def apply_filters(
        query: Select,
        model: Type,
        filters: dict[str, Any],
        allowed_fields: set[str]
    ) -> Select:
        """
        Apply dynamic filters to query with security and operation support.

        Filter format: {field}__operation = value
        Examples:
            - {'status__eq': 'active'}
            - {'created_at__gte': '2024-01-01'}
            - {'title__like': 'todo'}
            - {'id__in': [1, 2, 3]}

        Args:
            query: SQLAlchemy Select query
            model: SQLAlchemy model class
            filters: Dictionary of filters
            allowed_fields: Whitelist of fields that can be filtered

        Returns:
            Modified query with filters applied
        """
        for filter_key, value in filters.items():
            # Parse field__operation format
            if '__' in filter_key:
                field, operation = filter_key.rsplit('__', 1)
            else:
                field, operation = filter_key, 'eq'

            # Security: only allow whitelisted fields
            if field not in allowed_fields:
                continue

            # Check if field exists on model
            if not hasattr(model, field):
                continue

            # Check if operation is supported
            if operation not in QueryHelper.ALLOWED_OPERATIONS:
                continue

            column = getattr(model, field)
            operation_func = QueryHelper.ALLOWED_OPERATIONS[operation]
            query = query.filter(operation_func(column, value))

        return query

    @staticmethod
    def apply_sorting(
        query: Select,
        model: Type,
        sort_by: str,
        order: str = "asc",
        allowed_fields: set[str] | None = None
    ) -> Select:
        """
        Apply sorting to query.

        Args:
            query: SQLAlchemy Select query
            model: SQLAlchemy model class
            sort_by: Field to sort by
            order: 'asc' or 'desc'
            allowed_fields: Optional whitelist of sortable fields

        Returns:
            Modified query with sorting applied
        """
        # Security: only allow whitelisted fields if provided
        if allowed_fields and sort_by not in allowed_fields:
            return query

        if not hasattr(model, sort_by):
            return query

        column = getattr(model, sort_by)
        if order.lower() == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

        return query

    @staticmethod
    def apply_pagination(query: Select, page: int, page_size: int, max_page_size: int = 100) -> Select:
        """
        Apply pagination to query.

        Args:
            query: SQLAlchemy Select query
            page: Page number (1-indexed)
            page_size: Number of items per page
            max_page_size: Maximum allowed page size

        Returns:
            Modified query with pagination applied
        """
        # Validate and cap page_size
        page_size = min(page_size, max_page_size)
        page_size = max(page_size, 1)  # At least 1 item

        # Ensure page is at least 1
        page = max(page, 1)

        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)
```

**Pagination Helper** (`core/database/pagination.py`):

```python
from typing import TypeVar, Generic
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')

class PaginationMetadata(BaseModel):
    """Pagination metadata for API responses"""
    page: int
    page_size: int
    total: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: list[T]
    pagination: PaginationMetadata

def create_pagination_metadata(
    page: int,
    page_size: int,
    total: int
) -> PaginationMetadata:
    """Create pagination metadata from query results"""
    return PaginationMetadata(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if page_size > 0 else 0
    )
```

**Feature Repository Example** (`features/todos/repository.py`):

```python
from typing import Any
from sqlalchemy import select, func
from core.database.base_repository import BaseRepository
from core.database.query_helper import QueryHelper
from core.database.pagination import PaginatedResponse, create_pagination_metadata
from .models import Todo
from .schemas import TodoResponse

class TodoRepository(BaseRepository[Todo]):
    """Todo-specific repository inheriting common CRUD"""

    # Define allowed fields for filtering and sorting (security)
    FILTERABLE_FIELDS = {'title', 'completed', 'created_at', 'updated_at'}
    SORTABLE_FIELDS = {'title', 'created_at', 'updated_at', 'id'}

    async def search(
        self,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[TodoResponse]:
        """
        Search todos with dynamic filters, sorting, and pagination.

        Args:
            filters: Filter dict with format {field}__operation: value
                     e.g., {'completed__eq': True, 'title__like': 'urgent'}
            sort_by: Field to sort by (must be in SORTABLE_FIELDS)
            sort_order: 'asc' or 'desc'
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            PaginatedResponse with items and pagination metadata
        """
        # Build base query
        query = select(self.model)

        # Apply filters with security whitelist
        if filters:
            query = QueryHelper.apply_filters(
                query, self.model, filters, self.FILTERABLE_FIELDS
            )

        # Get total count BEFORE pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting with security whitelist
        if sort_by:
            query = QueryHelper.apply_sorting(
                query, self.model, sort_by, sort_order, self.SORTABLE_FIELDS
            )

        # Apply pagination
        query = QueryHelper.apply_pagination(query, page, page_size)

        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Create pagination metadata
        pagination = create_pagination_metadata(page, page_size, total)

        return PaginatedResponse(items=items, pagination=pagination)

    async def get_by_title(self, title: str) -> Todo | None:
        """Custom query for specific need"""
        result = await self.db.execute(
            select(self.model).filter(Todo.title == title)
        )
        return result.scalar_one_or_none()

    async def get_completed(self, limit: int = 10) -> list[Todo]:
        """Get recently completed todos"""
        result = await self.db.execute(
            select(self.model)
            .filter(Todo.completed == True)
            .order_by(Todo.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

**Database Rules:**

- All repositories MUST inherit from `BaseRepository[Model]`
- Use `QueryHelper` for dynamic filtering, sorting, and pagination from API params
- Define `FILTERABLE_FIELDS` and `SORTABLE_FIELDS` class attributes for security whitelisting
- Always get total count BEFORE applying pagination for accurate pagination metadata
- Use async database connections with SQLAlchemy AsyncSession
- Implement connection pooling in `core/database/session.py`
- Always use dependency injection for database sessions

**Pagination:**

- Default page size: 20 items
- Maximum page size: 100 items
- Use `PaginatedResponse` for consistent pagination structure
- Always include total count and total pages in response

### Service Layer & Business Logic

**Service vs Repository Separation:**

- **Repositories** = Data access only (CRUD, queries)
- **Services** = Business logic, orchestration, validation, multi-repository operations

**Service Example** (`features/todos/service.py`):

```python
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import ValidationException, NotFoundException
from core.database.pagination import PaginatedResponse
from .repository import TodoRepository
from .models import Todo
from .schemas import TodoCreate, TodoUpdate, TodoResponse

class TodoService:
    """Business logic for todo operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TodoRepository(Todo, db)

    async def create_todo(self, data: TodoCreate) -> TodoResponse:
        """
        Create a new todo with business logic validation.

        Business rules:
        - Title must be unique
        - Title cannot be empty or whitespace only
        """
        # Business validation
        if not data.title or not data.title.strip():
            raise ValidationException("Title cannot be empty")

        # Check uniqueness (business rule)
        existing = await self.repo.get_by_title(data.title)
        if existing:
            raise ValidationException(f"Todo with title '{data.title}' already exists")

        # Create entity
        todo = Todo(**data.model_dump())
        created = await self.repo.create(todo)

        return TodoResponse.model_validate(created)

    async def update_todo(self, todo_id: int, data: TodoUpdate) -> TodoResponse:
        """Update todo with business validation"""
        # Business validation
        if data.title and not data.title.strip():
            raise ValidationException("Title cannot be empty")

        # Check if title is being changed to an existing one
        if data.title:
            existing = await self.repo.get_by_title(data.title)
            if existing and existing.id != todo_id:
                raise ValidationException(f"Todo with title '{data.title}' already exists")

        # Update using repository
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repo.update(todo_id, update_data)

        return TodoResponse.model_validate(updated)

    async def delete_todo(self, todo_id: int) -> None:
        """Delete todo"""
        await self.repo.delete(todo_id)

    async def get_todo(self, todo_id: int) -> TodoResponse:
        """Get single todo by ID"""
        todo = await self.repo.get_or_404(todo_id)
        return TodoResponse.model_validate(todo)

    async def search_todos(
        self,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[TodoResponse]:
        """Search todos with pagination"""
        return await self.repo.search(filters, sort_by, sort_order, page, page_size)

    async def mark_completed(self, todo_id: int) -> TodoResponse:
        """
        Mark todo as completed (business operation).

        This is a business operation, not just a data update.
        Could trigger side effects like notifications, logging, etc.
        """
        todo = await self.repo.get_or_404(todo_id)

        # Business logic: prevent re-completing
        if todo.completed:
            raise ValidationException("Todo is already completed")

        # Update
        updated = await self.repo.update(todo_id, {"completed": True})

        # Business logic: could trigger side effects here
        # await self.notification_service.send_completion_notification(updated)
        # await self.analytics_service.track_completion(updated)

        return TodoResponse.model_validate(updated)
```

**Service Layer Rules:**

- Services contain business logic and validation
- Services can orchestrate multiple repositories
- Services should NOT import other feature's services (to avoid coupling)
- Use domain events or shared services for cross-feature communication
- Services manage transaction boundaries for multi-step operations

### Transaction Management

**Strategy: Service-Managed Transactions**

The database session is injected into services via dependency injection. By default, FastAPI's dependency system ensures the session is committed/rolled back automatically.

**For Multi-Step Operations:**

```python
# features/todos/service.py
class TodoService:
    async def create_todo_with_subtasks(
        self,
        todo_data: TodoCreate,
        subtask_data: list[SubtaskCreate]
    ) -> TodoResponse:
        """
        Create todo with subtasks in a single transaction.

        If any step fails, the entire transaction is rolled back.
        """
        try:
            # Create main todo
            todo = Todo(**todo_data.model_dump())
            created_todo = await self.repo.create(todo)

            # Create subtasks
            for subtask in subtask_data:
                subtask_obj = Subtask(**subtask.model_dump(), todo_id=created_todo.id)
                await self.subtask_repo.create(subtask_obj)

            # Commit happens automatically when function returns successfully
            return TodoResponse.model_validate(created_todo)

        except Exception as e:
            # Rollback happens automatically on exception
            # Session is managed by FastAPI dependency
            raise

# If you need manual transaction control:
async def complex_operation(self):
    """Manual transaction control for complex scenarios"""
    try:
        # Do work...
        await self.db.commit()
    except Exception:
        await self.db.rollback()
        raise
```

### Dependency Injection

**Database Session Setup** (`core/database/session.py`):

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency for database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Dependency Injection Setup** (`core/dependencies.py`):

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.session import get_db

# Type alias for cleaner dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

# Example: Repository dependency
def get_todo_repository(db: DatabaseSession) -> TodoRepository:
    """Dependency for TodoRepository"""
    from features.todos.repository import TodoRepository
    from features.todos.models import Todo
    return TodoRepository(Todo, db)

# Example: Service dependency
def get_todo_service(db: DatabaseSession) -> TodoService:
    """Dependency for TodoService"""
    from features.todos.service import TodoService
    return TodoService(db)
```

**API Route with Dependency Injection** (`features/todos/api.py`):

```python
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from core.dependencies import DatabaseSession
from core.schemas import APIResponse
from .service import TodoService
from .schemas import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

# Dependency for service
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]

@router.post("", response_model=APIResponse[TodoResponse], status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    service: TodoServiceDep,
) -> APIResponse[TodoResponse]:
    """Create a new todo"""
    todo = await service.create_todo(data)
    return APIResponse(data=todo)

@router.get("/{todo_id}", response_model=APIResponse[TodoResponse])
async def get_todo(
    todo_id: int,
    service: TodoServiceDep,
) -> APIResponse[TodoResponse]:
    """Get a single todo by ID"""
    todo = await service.get_todo(todo_id)
    return APIResponse(data=todo)

@router.get("", response_model=APIResponse[PaginatedResponse[TodoResponse]])
async def search_todos(
    service: TodoServiceDep,
    completed: bool | None = Query(None),
    title: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> APIResponse[PaginatedResponse[TodoResponse]]:
    """Search todos with filtering, sorting, and pagination"""
    # Build filters from query params
    filters = {}
    if completed is not None:
        filters['completed__eq'] = completed
    if title:
        filters['title__ilike'] = title

    result = await service.search_todos(filters, sort_by, sort_order, page, page_size)
    return APIResponse(data=result)

@router.put("/{todo_id}", response_model=APIResponse[TodoResponse])
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    service: TodoServiceDep,
) -> APIResponse[TodoResponse]:
    """Update a todo"""
    todo = await service.update_todo(todo_id, data)
    return APIResponse(data=todo)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodoServiceDep,
) -> None:
    """Delete a todo"""
    await service.delete_todo(todo_id)

@router.post("/{todo_id}/complete", response_model=APIResponse[TodoResponse])
async def mark_todo_completed(
    todo_id: int,
    service: TodoServiceDep,
) -> APIResponse[TodoResponse]:
    """Mark a todo as completed"""
    todo = await service.mark_completed(todo_id)
    return APIResponse(data=todo)
```

### Testing

**Test structure:**
- Place tests alongside the feature in `features/{feature_name}/tests/`
- Name test files: `test_{module_name}.py`
- Use descriptive test names: `test_create_todo_returns_201_when_valid_data()`

**Test requirements:**
- Unit tests for all business logic
- Integration tests for API endpoints
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common test data

### File Organization

**Feature Structure:**

When creating new features:

1. Create a new directory under `features/`
2. Include all feature-specific code in that directory
3. Keep features independent and loosely coupled
4. Tests MUST be alongside the feature in `features/{feature_name}/tests/`

**File Naming Conventions:**

- `schemas.py` - Pydantic models for API request/response (NOT `models.py`)
- `models.py` - SQLAlchemy models for database tables
- `api.py` - FastAPI route handlers
- `service.py` - Business logic layer
- `repository.py` - Data access layer (inherits from BaseRepository)
- `exceptions.py` - Feature-specific exception classes

**Example:**

```python
# features/todos/schemas.py - Pydantic (API layer)
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool

# features/todos/models.py - SQLAlchemy (Database layer)
from sqlalchemy.orm import Mapped, mapped_column
from core.database.base import Base

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None]
    completed: Mapped[bool] = mapped_column(default=False)
```

**Shared Code Guidelines:**

**DO NOT extract to `shared/` prematurely.** Follow the "Rule of Three":

- Keep code in the feature directory until 3+ features need it
- Only then extract to `shared/`
- This prevents premature abstraction and tight coupling

**What belongs in `shared/`:**

- Infrastructure-level enums (e.g., `Environment`, `LogLevel`, `HttpMethod`)
- Truly cross-cutting utility functions (e.g., date formatting, string helpers)
- Application-wide constants

**What does NOT belong in `shared/`:**

- Domain-specific enums (e.g., `TodoStatus`, `UserRole`) - keep in features
- Business logic - belongs in feature services
- Feature-specific utilities - keep in the feature directory

**Example:**

```python
# ✅ GOOD - Infrastructure enum in shared/enums.py
class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# ❌ BAD - Domain enum should stay in features/todos/
class TodoStatus(str, Enum):  # Keep this in features/todos/enums.py
    PENDING = "pending"
    COMPLETED = "completed"
```

## Key Patterns Summary

### Request Flow

```
HTTP Request
    ↓
Request Tracking Middleware (add request_id, timestamp)
    ↓
Error Handling Middleware (catch all exceptions)
    ↓
FastAPI Router (features/todos/api.py)
    ↓
Dependency Injection (get database session, service)
    ↓
Service Layer (business logic, validation)
    ↓
Repository Layer (data access via BaseRepository + QueryHelper)
    ↓
Database (PostgreSQL via SQLAlchemy async)
    ↓
Response (wrapped in APIResponse with meta)
```

### Layer Responsibilities

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **API (api.py)** | Route definition, request parsing, response formatting | `@router.post("/todos")` |
| **Service (service.py)** | Business logic, validation, orchestration | `if not title.strip(): raise ValidationException` |
| **Repository (repository.py)** | Data access, queries | `await self.repo.get(id)` |
| **Models (models.py)** | Database schema (SQLAlchemy) | `class Todo(Base)` |
| **Schemas (schemas.py)** | API contracts (Pydantic) | `class TodoCreate(BaseModel)` |

### Security Checklist

✅ **Always whitelist filterable/sortable fields** in repositories
✅ **Never expose internal errors** to API responses
✅ **Use type hints** on all functions
✅ **Validate business rules** in service layer
✅ **Use dependency injection** for database sessions
✅ **Catch exceptions** in error handling middleware
✅ **Track all requests** with unique IDs
✅ **Log errors** with request context

### Common Patterns

**Creating a new feature:**

1. Create directory: `features/{feature_name}/`
2. Add SQLAlchemy models: `models.py`
3. Add Pydantic schemas: `schemas.py`
4. Add repository (inherit BaseRepository): `repository.py`
5. Add service (business logic): `service.py`
6. Add API routes: `api.py`
7. Add tests: `tests/`
8. Register router in `main.py`

**Adding a new endpoint:**

1. Write test first (TDD)
2. Add Pydantic schemas for request/response
3. Add business logic to service
4. Add route to `api.py` with dependency injection
5. Return `APIResponse[YourSchema]`
6. Run tests and verify

**Adding filtering to a feature:**

1. Define `FILTERABLE_FIELDS` in repository
2. Use QueryHelper in `search()` method
3. Accept filters dict in service method
4. Build filters from query params in API route
5. Use format: `{'field__operation': value}`

## Quick Reference

**Common imports:**

```python
# API layer
from fastapi import APIRouter, Depends, Query, status
from core.schemas import APIResponse
from core.dependencies import DatabaseSession

# Service layer
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import ValidationException, NotFoundException

# Repository layer
from sqlalchemy import select, func
from core.database.base_repository import BaseRepository
from core.database.query_helper import QueryHelper

# Models
from sqlalchemy.orm import Mapped, mapped_column
from core.database.session import Base

# Schemas
from pydantic import BaseModel, Field
```

**Filter operations:**

- `field__eq` - Equal
- `field__ne` - Not equal
- `field__gt` - Greater than
- `field__gte` - Greater than or equal
- `field__lt` - Less than
- `field__lte` - Less than or equal
- `field__like` - Case-sensitive LIKE
- `field__ilike` - Case-insensitive LIKE
- `field__in` - IN list
- `field__not_in` - NOT IN list
- `field__is_null` - IS NULL / IS NOT NULL
