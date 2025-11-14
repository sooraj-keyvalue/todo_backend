"""
Test health check endpoints.
Simple tests to verify the test infrastructure is working.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient) -> None:
    """Test liveness probe endpoint."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    """Test readiness probe endpoint."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "environment" in data
    assert data["docs"] == "/docs"
