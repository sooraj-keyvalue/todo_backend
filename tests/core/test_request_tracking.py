"""
Tests for request tracking middleware.
Verifies UUID generation, request.state population, and response headers.
"""

from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_in_response_header(client: AsyncClient) -> None:
    """Test that X-Request-ID header is added to response."""
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_request_id_is_valid_uuid(client: AsyncClient) -> None:
    """Test that X-Request-ID is a valid UUID."""
    response = await client.get("/health/live")

    request_id = response.headers["X-Request-ID"]
    # This will raise ValueError if not a valid UUID
    uuid_obj = UUID(request_id)
    assert str(uuid_obj) == request_id


@pytest.mark.asyncio
async def test_different_requests_have_different_ids(
    client: AsyncClient,
) -> None:
    """Test that different requests get different request IDs."""
    response1 = await client.get("/health/live")
    response2 = await client.get("/health/live")

    request_id1 = response1.headers["X-Request-ID"]
    request_id2 = response2.headers["X-Request-ID"]

    assert request_id1 != request_id2


@pytest.mark.asyncio
async def test_existing_request_id_is_preserved(client: AsyncClient) -> None:
    """Test that existing X-Request-ID header is preserved."""
    custom_id = "12345678-1234-5678-1234-567812345678"

    response = await client.get(
        "/health/live",
        headers={"X-Request-ID": custom_id},
    )

    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_request_id_on_different_endpoints(client: AsyncClient) -> None:
    """Test that all endpoints get request IDs."""
    endpoints = [
        "/health/live",
        "/health/ready",
        "/",
    ]

    for endpoint in endpoints:
        response = await client.get(endpoint)
        assert "X-Request-ID" in response.headers
        # Verify it's a valid UUID
        UUID(response.headers["X-Request-ID"])


@pytest.mark.asyncio
async def test_request_id_on_different_methods(client: AsyncClient) -> None:
    """Test that all HTTP methods get request IDs."""
    # GET
    response = await client.get("/health/live")
    assert "X-Request-ID" in response.headers

    # Note: We'll add more methods when we have POST/PUT/DELETE endpoints


@pytest.mark.asyncio
async def test_request_id_on_error_response(client: AsyncClient) -> None:
    """Test that request ID is present even on error responses."""
    # Request a non-existent endpoint
    response = await client.get("/non-existent-endpoint")

    # Should be 404
    assert response.status_code == 404
    # But should still have request ID
    assert "X-Request-ID" in response.headers
    UUID(response.headers["X-Request-ID"])


@pytest.mark.asyncio
async def test_multiple_requests_in_sequence(client: AsyncClient) -> None:
    """Test that multiple sequential requests all get unique IDs."""
    request_ids = set()

    for _ in range(5):
        response = await client.get("/health/live")
        request_id = response.headers["X-Request-ID"]
        request_ids.add(request_id)

    # All IDs should be unique
    assert len(request_ids) == 5
