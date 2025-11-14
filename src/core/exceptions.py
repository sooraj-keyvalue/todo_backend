"""
Custom exception classes for the application.
Provides structured error handling with HTTP status codes.
"""

from typing import Any


class BaseAPIException(Exception):
    """
    Base exception for all API errors.

    All custom exceptions should inherit from this class.
    Provides standard structure for error handling.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        status_code: HTTP status code
        details: Optional additional error details
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code (default: 500)
            details: Optional additional error details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        """String representation of the exception."""
        return f"{self.code}: {self.message}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code})"
        )


class NotFoundException(BaseAPIException):
    """
    Exception raised when a resource is not found.

    HTTP Status: 404 Not Found

    Example:
        ```python
        raise NotFoundException(
            message="Task with id 123 not found",
            code="TASK_NOT_FOUND"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize NotFoundException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: NOT_FOUND)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=404,
            details=details,
        )


class AuthenticationException(BaseAPIException):
    """
    Exception raised when authentication fails.

    HTTP Status: 401 Unauthorized

    Example:
        ```python
        raise AuthenticationException(
            message="Invalid credentials",
            code="INVALID_CREDENTIALS"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_FAILED",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize AuthenticationException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: AUTHENTICATION_FAILED)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details,
        )


class AuthorizationException(BaseAPIException):
    """
    Exception raised when user lacks permission.

    HTTP Status: 403 Forbidden

    Example:
        ```python
        raise AuthorizationException(
            message="You don't have permission to delete this task",
            code="PERMISSION_DENIED"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "PERMISSION_DENIED",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize AuthorizationException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: PERMISSION_DENIED)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details,
        )


class ValidationException(BaseAPIException):
    """
    Exception raised when input validation fails.

    HTTP Status: 422 Unprocessable Entity

    Example:
        ```python
        raise ValidationException(
            message="Invalid input data",
            code="VALIDATION_ERROR",
            details={
                "email": "Invalid email format",
                "password": "Password too short"
            }
        )
        ```
    """

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize ValidationException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: VALIDATION_ERROR)
            details: Dictionary of field-level validation errors
        """
        super().__init__(
            message=message,
            code=code,
            status_code=422,
            details=details,
        )


class ConflictException(BaseAPIException):
    """
    Exception raised when a resource conflict occurs.

    HTTP Status: 409 Conflict

    Example:
        ```python
        raise ConflictException(
            message="User with this email already exists",
            code="USER_ALREADY_EXISTS"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize ConflictException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: CONFLICT)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=409,
            details=details,
        )


class BadRequestException(BaseAPIException):
    """
    Exception raised for malformed or invalid requests.

    HTTP Status: 400 Bad Request

    Example:
        ```python
        raise BadRequestException(
            message="Invalid request format",
            code="BAD_REQUEST"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize BadRequestException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: BAD_REQUEST)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            details=details,
        )


class InternalServerException(BaseAPIException):
    """
    Exception raised for internal server errors.

    HTTP Status: 500 Internal Server Error

    Example:
        ```python
        raise InternalServerException(
            message="An unexpected error occurred",
            code="INTERNAL_ERROR"
        )
        ```
    """

    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize InternalServerException.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (default: INTERNAL_ERROR)
            details: Optional additional error details
        """
        super().__init__(
            message=message,
            code=code,
            status_code=500,
            details=details,
        )
