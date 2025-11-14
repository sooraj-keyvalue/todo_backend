"""
Error handling middleware.
Catches all exceptions and converts them to standardized ErrorResponse.
"""

import logging
from datetime import datetime, timezone

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.exceptions import BaseAPIException
from src.core.schemas import ErrorDetail, ErrorResponse, ResponseMetadata

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle all exceptions globally.

    Catches exceptions and converts them to standardized ErrorResponse format:
    - Custom BaseAPIException: Uses exception's status code and details
    - Validation errors: Returns 422 with field-level errors
    - Unknown exceptions: Returns 500 Internal Server Error

    All error responses include request tracking metadata.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and handle any exceptions.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response (either success or error)
        """
        try:
            # Process the request
            response = await call_next(request)
            return response

        except BaseAPIException as exc:
            # Handle our custom exceptions
            logger.warning(
                f"API Exception: {exc.code} - {exc.message}",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": exc.status_code,
                    "error_code": exc.code,
                },
            )

            return self._create_error_response(
                request=request,
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
            )

        except Exception as exc:
            # Handle unexpected exceptions
            logger.error(
                f"Unhandled exception: {str(exc)}",
                exc_info=True,
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "path": request.url.path,
                    "method": request.method,
                },
            )

            return self._create_error_response(
                request=request,
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                status_code=500,
                details=None,
            )

    def _create_error_response(
        self,
        request: Request,
        code: str,
        message: str,
        status_code: int,
        details: dict | None = None,
    ) -> JSONResponse:
        """
        Create a standardized error response.

        Args:
            request: The request that caused the error
            code: Machine-readable error code
            message: Human-readable error message
            status_code: HTTP status code
            details: Optional additional error details

        Returns:
            JSONResponse with ErrorResponse format
        """
        # Create error response with metadata
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details,
            ),
            meta=ResponseMetadata(
                request_id=getattr(request.state, "request_id", "unknown"),
                timestamp=getattr(
                    request.state, "timestamp", datetime.now(timezone.utc)
                ),
                path=getattr(request.state, "path", request.url.path),
                method=getattr(request.state, "method", request.method),
            ),
        )

        return JSONResponse(
            status_code=status_code,
            content=error_response.model_dump(mode="json"),
        )
