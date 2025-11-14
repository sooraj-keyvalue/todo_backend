"""
Test router for error handling verification.
Only available in DEBUG mode.
Provides endpoints to test various exception types.
"""

from fastapi import APIRouter

from src.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BadRequestException,
    ConflictException,
    NotFoundException,
    ValidationException,
)

router = APIRouter(prefix="/test/error", tags=["Test"])


@router.get("/not-found", include_in_schema=False)
async def test_not_found() -> None:
    """Test endpoint that raises NotFoundException."""
    raise NotFoundException(message="Test resource not found")


@router.get("/validation", include_in_schema=False)
async def test_validation() -> None:
    """Test endpoint that raises ValidationException."""
    raise ValidationException(
        message="Test validation failed",
        details={"field": "test_field", "error": "test error"},
    )


@router.get("/auth", include_in_schema=False)
async def test_authentication() -> None:
    """Test endpoint that raises AuthenticationException."""
    raise AuthenticationException(message="Test authentication failed")


@router.get("/forbidden", include_in_schema=False)
async def test_authorization() -> None:
    """Test endpoint that raises AuthorizationException."""
    raise AuthorizationException(message="Test permission denied")


@router.get("/conflict", include_in_schema=False)
async def test_conflict() -> None:
    """Test endpoint that raises ConflictException."""
    raise ConflictException(message="Test resource conflict")


@router.get("/bad-request", include_in_schema=False)
async def test_bad_request() -> None:
    """Test endpoint that raises BadRequestException."""
    raise BadRequestException(message="Test bad request")


@router.get("/internal", include_in_schema=False)
async def test_internal_error() -> None:
    """Test endpoint that raises unexpected exception."""
    raise ValueError("Test unexpected error")
