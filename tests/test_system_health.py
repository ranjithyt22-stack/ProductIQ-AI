"""
Unit and Integration Tests for System Health & Telemetry.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_system_health_endpoint(client):
    response = client.get("/api/v1/health/system")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["api_version"] == "2.5.0"
    assert "database" in data
    assert data["database"]["status"] == "connected"
    assert "ai_engine" in data
    assert data["ai_engine"]["provider"] == "Ollama"
