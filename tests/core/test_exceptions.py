"""
Tests for custom exception classes.
Verifies exception hierarchy, attributes, and behavior.
"""

import pytest

from src.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BadRequestException,
    BaseAPIException,
    ConflictException,
    InternalServerException,
    NotFoundException,
    ValidationException,
)


def test_base_api_exception() -> None:
    """Test BaseAPIException creation and attributes."""
    exc = BaseAPIException(
        message="Test error",
        code="TEST_ERROR",
        status_code=500,
        details={"key": "value"},
    )

    assert exc.message == "Test error"
    assert exc.code == "TEST_ERROR"
    assert exc.status_code == 500
    assert exc.details == {"key": "value"}
    assert str(exc) == "TEST_ERROR: Test error"


def test_base_api_exception_repr() -> None:
    """Test BaseAPIException string representation."""
    exc = BaseAPIException(
        message="Test error",
        code="TEST_ERROR",
        status_code=500,
    )

    repr_str = repr(exc)
    assert "BaseAPIException" in repr_str
    assert "Test error" in repr_str
    assert "TEST_ERROR" in repr_str
    assert "500" in repr_str


def test_not_found_exception() -> None:
    """Test NotFoundException with default values."""
    exc = NotFoundException()

    assert exc.message == "Resource not found"
    assert exc.code == "NOT_FOUND"
    assert exc.status_code == 404
    assert exc.details is None


def test_not_found_exception_custom() -> None:
    """Test NotFoundException with custom values."""
    exc = NotFoundException(
        message="Task not found",
        code="TASK_NOT_FOUND",
        details={"task_id": "123"},
    )

    assert exc.message == "Task not found"
    assert exc.code == "TASK_NOT_FOUND"
    assert exc.status_code == 404
    assert exc.details == {"task_id": "123"}


def test_authentication_exception() -> None:
    """Test AuthenticationException with default values."""
    exc = AuthenticationException()

    assert exc.message == "Authentication failed"
    assert exc.code == "AUTHENTICATION_FAILED"
    assert exc.status_code == 401
    assert exc.details is None


def test_authentication_exception_custom() -> None:
    """Test AuthenticationException with custom values."""
    exc = AuthenticationException(
        message="Invalid credentials",
        code="INVALID_CREDENTIALS",
    )

    assert exc.message == "Invalid credentials"
    assert exc.code == "INVALID_CREDENTIALS"
    assert exc.status_code == 401


def test_authorization_exception() -> None:
    """Test AuthorizationException with default values."""
    exc = AuthorizationException()

    assert exc.message == "Permission denied"
    assert exc.code == "PERMISSION_DENIED"
    assert exc.status_code == 403
    assert exc.details is None


def test_authorization_exception_custom() -> None:
    """Test AuthorizationException with custom values."""
    exc = AuthorizationException(
        message="Cannot delete this resource",
        code="DELETE_FORBIDDEN",
    )

    assert exc.message == "Cannot delete this resource"
    assert exc.code == "DELETE_FORBIDDEN"
    assert exc.status_code == 403


def test_validation_exception() -> None:
    """Test ValidationException with default values."""
    exc = ValidationException()

    assert exc.message == "Validation failed"
    assert exc.code == "VALIDATION_ERROR"
    assert exc.status_code == 422
    assert exc.details is None


def test_validation_exception_with_details() -> None:
    """Test ValidationException with field-level errors."""
    details = {
        "email": "Invalid email format",
        "password": "Password too short",
    }

    exc = ValidationException(
        message="Invalid input data",
        details=details,
    )

    assert exc.message == "Invalid input data"
    assert exc.code == "VALIDATION_ERROR"
    assert exc.status_code == 422
    assert exc.details == details
    assert "email" in exc.details
    assert "password" in exc.details


def test_conflict_exception() -> None:
    """Test ConflictException with default values."""
    exc = ConflictException()

    assert exc.message == "Resource conflict"
    assert exc.code == "CONFLICT"
    assert exc.status_code == 409
    assert exc.details is None


def test_conflict_exception_custom() -> None:
    """Test ConflictException with custom values."""
    exc = ConflictException(
        message="Email already exists",
        code="EMAIL_EXISTS",
    )

    assert exc.message == "Email already exists"
    assert exc.code == "EMAIL_EXISTS"
    assert exc.status_code == 409


def test_bad_request_exception() -> None:
    """Test BadRequestException with default values."""
    exc = BadRequestException()

    assert exc.message == "Bad request"
    assert exc.code == "BAD_REQUEST"
    assert exc.status_code == 400
    assert exc.details is None


def test_bad_request_exception_custom() -> None:
    """Test BadRequestException with custom values."""
    exc = BadRequestException(
        message="Invalid JSON format",
        code="INVALID_JSON",
    )

    assert exc.message == "Invalid JSON format"
    assert exc.code == "INVALID_JSON"
    assert exc.status_code == 400


def test_internal_server_exception() -> None:
    """Test InternalServerException with default values."""
    exc = InternalServerException()

    assert exc.message == "Internal server error"
    assert exc.code == "INTERNAL_ERROR"
    assert exc.status_code == 500
    assert exc.details is None


def test_internal_server_exception_custom() -> None:
    """Test InternalServerException with custom values."""
    exc = InternalServerException(
        message="Database connection failed",
        code="DB_CONNECTION_ERROR",
    )

    assert exc.message == "Database connection failed"
    assert exc.code == "DB_CONNECTION_ERROR"
    assert exc.status_code == 500


def test_exception_inheritance() -> None:
    """Test that all exceptions inherit from BaseAPIException."""
    exceptions = [
        NotFoundException(),
        AuthenticationException(),
        AuthorizationException(),
        ValidationException(),
        ConflictException(),
        BadRequestException(),
        InternalServerException(),
    ]

    for exc in exceptions:
        assert isinstance(exc, BaseAPIException)
        assert isinstance(exc, Exception)


def test_exception_can_be_raised_and_caught() -> None:
    """Test that exceptions can be raised and caught."""
    with pytest.raises(NotFoundException) as exc_info:
        raise NotFoundException(message="Test not found")

    assert exc_info.value.message == "Test not found"
    assert exc_info.value.status_code == 404


def test_exception_can_be_caught_as_base() -> None:
    """Test that specific exceptions can be caught as BaseAPIException."""
    with pytest.raises(BaseAPIException) as exc_info:
        raise NotFoundException(message="Test not found")

    assert exc_info.value.message == "Test not found"
    assert exc_info.value.status_code == 404


def test_multiple_exceptions_have_different_status_codes() -> None:
    """Test that different exceptions have appropriate status codes."""
    status_codes = {
        BadRequestException(): 400,
        AuthenticationException(): 401,
        AuthorizationException(): 403,
        NotFoundException(): 404,
        ConflictException(): 409,
        ValidationException(): 422,
        InternalServerException(): 500,
    }

    for exc, expected_code in status_codes.items():
        assert exc.status_code == expected_code
