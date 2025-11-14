"""
Core response schemas for API responses.
Provides standard format for success and error responses with metadata.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

# Generic type variable for response data
T = TypeVar("T")


class ResponseMetadata(BaseModel):
    """
    Metadata included in all API responses.
    Provides request tracking and context information.
    """

    request_id: UUID = Field(
        ...,
        description="Unique identifier for this request",
        examples=["7f3e5c2a-1d4e-4b8a-9c3f-2e5d6a7b8c9d"],
    )
    timestamp: datetime = Field(
        ...,
        description="ISO 8601 timestamp when the response was generated",
        examples=["2024-01-15T10:30:00Z"],
    )
    path: str = Field(
        ...,
        description="API endpoint path that was called",
        examples=["/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000"],
    )
    method: str = Field(
        ...,
        description="HTTP method used for the request",
        examples=["GET", "POST", "PATCH", "DELETE"],
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "request_id": "7f3e5c2a-1d4e-4b8a-9c3f-2e5d6a7b8c9d",
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/tasks",
                "method": "GET",
            }
        }


class APIResponse(BaseModel, Generic[T]):
    """
    Standard success response wrapper.

    All successful API responses follow this format with data and metadata.

    Type Parameters:
        T: The type of data being returned

    Example:
        ```python
        response = APIResponse[TaskResponse](
            data=task_data,
            meta=ResponseMetadata(...)
        )
        ```
    """

    data: T = Field(
        ...,
        description="The actual response data",
    )
    meta: ResponseMetadata = Field(
        ...,
        description="Request metadata for tracking and debugging",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "data": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Buy groceries",
                    "is_completed": False,
                },
                "meta": {
                    "request_id": "7f3e5c2a-1d4e-4b8a-9c3f-2e5d6a7b8c9d",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "path": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000",
                    "method": "GET",
                },
            }
        }


class ErrorDetail(BaseModel):
    """
    Detailed error information.

    Provides structured error information with code, message, and optional details.
    """

    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["NOT_FOUND", "VALIDATION_ERROR", "UNAUTHORIZED"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Task with id 550e8400-e29b-41d4-a716-446655440000 not found"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details (e.g., validation errors)",
        examples=[{"field": "email", "error": "Invalid email format"}],
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {
                    "email": "Invalid email format",
                    "password": "Password must be at least 8 characters",
                },
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response wrapper.

    All error responses follow this format with error details and metadata.

    Example:
        ```python
        response = ErrorResponse(
            error=ErrorDetail(
                code="NOT_FOUND",
                message="Resource not found"
            ),
            meta=ResponseMetadata(...)
        )
        ```
    """

    error: ErrorDetail = Field(
        ...,
        description="Error information",
    )
    meta: ResponseMetadata = Field(
        ...,
        description="Request metadata for tracking and debugging",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Task with id 550e8400-e29b-41d4-a716-446655440000 not found",
                    "details": None,
                },
                "meta": {
                    "request_id": "7f3e5c2a-1d4e-4b8a-9c3f-2e5d6a7b8c9d",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "path": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000",
                    "method": "GET",
                },
            }
        }
