"""
FastAPI application entry point.
Main application with middleware, routers, and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.middleware.error_handling import ErrorHandlingMiddleware
from src.core.middleware.request_tracking import RequestTrackingMiddleware
from src.features.health import router as health_router
from src.features.root import router as root_router

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
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(root_router)
app.include_router(health_router)

# Include test router only in DEBUG mode
if settings.DEBUG:
    from src.features.test import router as test_router

    app.include_router(test_router)
