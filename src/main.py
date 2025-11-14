"""
FastAPI application entry point.
Main application with middleware, routers, and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.middleware.error_handling import ErrorHandlingMiddleware
from src.core.middleware.request_tracking import RequestTrackingMiddleware

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware (order matters: last added = first executed)
# 1. Error handling (outermost - catches all errors)
app.add_middleware(ErrorHandlingMiddleware)
# 2. Request tracking (tracks all requests, even errors)
app.add_middleware(RequestTrackingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=[settings.CORS_ALLOW_METHODS],
    allow_headers=[settings.CORS_ALLOW_HEADERS],
)


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> dict[str, str]:
    """
    Liveness probe endpoint.
    Returns 200 if the application is running.
    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict[str, str]:
    """
    Readiness probe endpoint.
    Returns 200 if the application is ready to serve requests.
    """
    return {"status": "ready"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


# Test endpoints for error handling (for testing purposes)
if settings.DEBUG:
    from src.core.exceptions import (
        AuthenticationException,
        AuthorizationException,
        BadRequestException,
        ConflictException,
        NotFoundException,
        ValidationException,
    )

    @app.get("/test/error/not-found", tags=["Test"], include_in_schema=False)
    async def test_not_found() -> None:
        """Test endpoint that raises NotFoundException."""
        raise NotFoundException(message="Test resource not found")

    @app.get("/test/error/validation", tags=["Test"], include_in_schema=False)
    async def test_validation() -> None:
        """Test endpoint that raises ValidationException."""
        raise ValidationException(
            message="Test validation failed",
            details={"field": "test_field", "error": "test error"},
        )

    @app.get("/test/error/auth", tags=["Test"], include_in_schema=False)
    async def test_authentication() -> None:
        """Test endpoint that raises AuthenticationException."""
        raise AuthenticationException(message="Test authentication failed")

    @app.get("/test/error/forbidden", tags=["Test"], include_in_schema=False)
    async def test_authorization() -> None:
        """Test endpoint that raises AuthorizationException."""
        raise AuthorizationException(message="Test permission denied")

    @app.get("/test/error/conflict", tags=["Test"], include_in_schema=False)
    async def test_conflict() -> None:
        """Test endpoint that raises ConflictException."""
        raise ConflictException(message="Test resource conflict")

    @app.get("/test/error/bad-request", tags=["Test"], include_in_schema=False)
    async def test_bad_request() -> None:
        """Test endpoint that raises BadRequestException."""
        raise BadRequestException(message="Test bad request")

    @app.get("/test/error/internal", tags=["Test"], include_in_schema=False)
    async def test_internal_error() -> None:
        """Test endpoint that raises unexpected exception."""
        raise ValueError("Test unexpected error")
