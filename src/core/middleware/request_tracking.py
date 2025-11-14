"""
Request tracking middleware.
Adds UUID-based request tracking to every request.
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with unique IDs.

    For each request:
    1. Generates a unique UUID (or uses existing X-Request-ID header)
    2. Stores tracking info in request.state
    3. Adds X-Request-ID header to response

    This enables request tracing across logs, errors, and responses.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and add tracking information.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response with X-Request-ID header
        """
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid4())

        # Store tracking information in request.state
        request.state.request_id = request_id
        request.state.timestamp = datetime.now(timezone.utc)
        request.state.path = request.url.path
        request.state.method = request.method

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
