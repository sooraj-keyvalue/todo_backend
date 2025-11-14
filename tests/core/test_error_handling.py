"""
Tests for error handling middleware.
Verifies exception catching and ErrorResponse format.
"""

from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_not_found_exception_handling(client: AsyncClient) -> None:
    """Test that NotFoundException returns 404 with ErrorResponse."""
    response = await client.get("/test/error/not-found")

    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert "meta" in data

    # Check error structure
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Test resource not found"
    assert data["error"]["details"] is None

    # Check metadata
    assert "request_id" in data["meta"]
    assert "timestamp" in data["meta"]
    assert data["meta"]["path"] == "/test/error/not-found"
    assert data["meta"]["method"] == "GET"

    # Verify request_id is valid UUID
    UUID(data["meta"]["request_id"])


@pytest.mark.asyncio
async def test_validation_exception_handling(client: AsyncClient) -> None:
    """Test that ValidationException returns 422 with details."""
    response = await client.get("/test/error/validation")

    assert response.status_code == 422

    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Test validation failed"
    assert data["error"]["details"] == {
        "field": "test_field",
        "error": "test error",
    }


@pytest.mark.asyncio
async def test_authentication_exception_handling(client: AsyncClient) -> None:
    """Test that AuthenticationException returns 401."""
    response = await client.get("/test/error/auth")

    assert response.status_code == 401

    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"
    assert data["error"]["message"] == "Test authentication failed"


@pytest.mark.asyncio
async def test_authorization_exception_handling(client: AsyncClient) -> None:
    """Test that AuthorizationException returns 403."""
    response = await client.get("/test/error/forbidden")

    assert response.status_code == 403

    data = response.json()
    assert data["error"]["code"] == "PERMISSION_DENIED"
    assert data["error"]["message"] == "Test permission denied"


@pytest.mark.asyncio
async def test_conflict_exception_handling(client: AsyncClient) -> None:
    """Test that ConflictException returns 409."""
    response = await client.get("/test/error/conflict")

    assert response.status_code == 409

    data = response.json()
    assert data["error"]["code"] == "CONFLICT"
    assert data["error"]["message"] == "Test resource conflict"


@pytest.mark.asyncio
async def test_bad_request_exception_handling(client: AsyncClient) -> None:
    """Test that BadRequestException returns 400."""
    response = await client.get("/test/error/bad-request")

    assert response.status_code == 400

    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"
    assert data["error"]["message"] == "Test bad request"


@pytest.mark.asyncio
async def test_internal_error_handling(client: AsyncClient) -> None:
    """Test that unexpected exceptions return 500."""
    response = await client.get("/test/error/internal")

    assert response.status_code == 500

    data = response.json()
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert data["error"]["message"] == "An unexpected error occurred"
    # Details should be None for security (don't expose internal errors)
    assert data["error"]["details"] is None


@pytest.mark.asyncio
async def test_error_response_has_request_id(client: AsyncClient) -> None:
    """Test that all error responses include request ID."""
    response = await client.get("/test/error/not-found")

    assert "X-Request-ID" in response.headers

    data = response.json()
    # Request ID in header should match metadata
    assert response.headers["X-Request-ID"] == data["meta"]["request_id"]


@pytest.mark.asyncio
async def test_error_response_preserves_custom_request_id(
    client: AsyncClient,
) -> None:
    """Test that custom request IDs are preserved in errors."""
    custom_id = "12345678-1234-5678-1234-567812345678"

    response = await client.get(
        "/test/error/not-found",
        headers={"X-Request-ID": custom_id},
    )

    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == custom_id

    data = response.json()
    assert data["meta"]["request_id"] == custom_id


@pytest.mark.asyncio
async def test_multiple_error_types_have_correct_status_codes(
    client: AsyncClient,
) -> None:
    """Test that different exceptions map to correct HTTP status codes."""
    test_cases = [
        ("/test/error/bad-request", 400),
        ("/test/error/auth", 401),
        ("/test/error/forbidden", 403),
        ("/test/error/not-found", 404),
        ("/test/error/conflict", 409),
        ("/test/error/validation", 422),
        ("/test/error/internal", 500),
    ]

    for endpoint, expected_status in test_cases:
        response = await client.get(endpoint)
        assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_error_response_format_is_consistent(
    client: AsyncClient,
) -> None:
    """Test that all errors follow the same response format."""
    endpoints = [
        "/test/error/not-found",
        "/test/error/validation",
        "/test/error/auth",
    ]

    for endpoint in endpoints:
        response = await client.get(endpoint)
        data = response.json()

        # All should have error and meta
        assert "error" in data
        assert "meta" in data

        # Error should have code, message, details
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]

        # Meta should have request_id, timestamp, path, method
        assert "request_id" in data["meta"]
        assert "timestamp" in data["meta"]
        assert "path" in data["meta"]
        assert "method" in data["meta"]


@pytest.mark.asyncio
async def test_success_responses_not_affected(client: AsyncClient) -> None:
    """Test that successful responses are not modified by error middleware."""
    response = await client.get("/health/live")

    assert response.status_code == 200
    data = response.json()

    # Should be the original response, not ErrorResponse format
    assert "status" in data
    assert data["status"] == "alive"
    assert "error" not in data
