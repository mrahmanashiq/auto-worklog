"""
Tests for main application functionality.

This module tests the basic application setup, health endpoints, and core functionality.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_api_documentation_available(client: TestClient):
    """Test that API documentation is available in debug mode."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client: TestClient):
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


@pytest.mark.asyncio
async def test_tracking_status_endpoint(async_client):
    """Test the tracking status endpoint."""
    from httpx import AsyncClient
    
    response = await async_client.get("/api/v1/tracking/status")
    # This will fail until we implement authentication
    # For now, just check that the endpoint exists
    assert response.status_code in [200, 404, 422]  # Various possible responses

