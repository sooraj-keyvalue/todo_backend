"""
Tests for core response schemas.
Verifies that APIResponse and ErrorResponse work correctly.
"""

from datetime import datetime, timezone
from uuid import uuid4

from src.core.schemas import (
    APIResponse,
    ErrorDetail,
    ErrorResponse,
    ResponseMetadata,
)


def test_response_metadata_creation() -> None:
    """Test creating ResponseMetadata."""
    request_id = uuid4()
    timestamp = datetime.now(timezone.utc)

    metadata = ResponseMetadata(
        request_id=request_id,
        timestamp=timestamp,
        path="/api/v1/tasks",
        method="GET",
    )

    assert metadata.request_id == request_id
    assert metadata.timestamp == timestamp
    assert metadata.path == "/api/v1/tasks"
    assert metadata.method == "GET"


def test_api_response_with_dict() -> None:
    """Test APIResponse with dict data."""
    data = {"id": "123", "title": "Test Task"}
    metadata = ResponseMetadata(
        request_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        path="/api/v1/tasks",
        method="GET",
    )

    response = APIResponse[dict](data=data, meta=metadata)

    assert response.data == data
    assert response.meta == metadata


def test_api_response_with_list() -> None:
    """Test APIResponse with list data."""
    data = [
        {"id": "1", "title": "Task 1"},
        {"id": "2", "title": "Task 2"},
    ]
    metadata = ResponseMetadata(
        request_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        path="/api/v1/tasks",
        method="GET",
    )

    response = APIResponse[list](data=data, meta=metadata)

    assert response.data == data
    assert len(response.data) == 2


def test_api_response_serialization() -> None:
    """Test that APIResponse can be serialized to JSON."""
    data = {"id": "123", "title": "Test Task"}
    metadata = ResponseMetadata(
        request_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        path="/api/v1/tasks",
        method="GET",
    )

    response = APIResponse[dict](data=data, meta=metadata)
    json_data = response.model_dump()

    assert "data" in json_data
    assert "meta" in json_data
    assert json_data["data"] == data


def test_error_detail_creation() -> None:
    """Test creating ErrorDetail."""
    error = ErrorDetail(
        code="NOT_FOUND",
        message="Resource not found",
        details=None,
    )

    assert error.code == "NOT_FOUND"
    assert error.message == "Resource not found"
    assert error.details is None


def test_error_detail_with_details() -> None:
    """Test ErrorDetail with validation details."""
    details = {
        "email": "Invalid email format",
        "password": "Password too short",
    }

    error = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Invalid input data",
        details=details,
    )

    assert error.code == "VALIDATION_ERROR"
    assert error.details == details
    assert "email" in error.details


def test_error_response_creation() -> None:
    """Test creating ErrorResponse."""
    error = ErrorDetail(
        code="NOT_FOUND",
        message="Task not found",
    )
    metadata = ResponseMetadata(
        request_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        path="/api/v1/tasks/123",
        method="GET",
    )

    response = ErrorResponse(error=error, meta=metadata)

    assert response.error == error
    assert response.meta == metadata


def test_error_response_serialization() -> None:
    """Test that ErrorResponse can be serialized to JSON."""
    error = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Invalid data",
        details={"field": "email"},
    )
    metadata = ResponseMetadata(
        request_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        path="/api/v1/users",
        method="POST",
    )

    response = ErrorResponse(error=error, meta=metadata)
    json_data = response.model_dump()

    assert "error" in json_data
    assert "meta" in json_data
    assert json_data["error"]["code"] == "VALIDATION_ERROR"
    assert json_data["error"]["details"] == {"field": "email"}


def test_response_metadata_json_example() -> None:
    """Test that ResponseMetadata has proper JSON schema example."""
    schema = ResponseMetadata.model_json_schema()
    assert "example" in schema or "examples" in schema


def test_api_response_generic_type() -> None:
    """Test that APIResponse works with different generic types."""
    # Test with string
    response_str = APIResponse[str](
        data="test",
        meta=ResponseMetadata(
            request_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            path="/test",
            method="GET",
        ),
    )
    assert isinstance(response_str.data, str)

    # Test with int
    response_int = APIResponse[int](
        data=42,
        meta=ResponseMetadata(
            request_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            path="/test",
            method="GET",
        ),
    )
    assert isinstance(response_int.data, int)
