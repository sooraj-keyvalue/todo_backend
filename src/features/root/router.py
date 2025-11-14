"""
Root router.
Provides API information and metadata endpoints.
"""

from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(tags=["Root"])


@router.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.

    Returns basic information about the API including name, version,
    environment, and documentation links.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }
