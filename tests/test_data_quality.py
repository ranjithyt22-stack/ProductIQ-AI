"""
Unit and Integration Tests for Data Quality Operations.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_data_quality_overview_endpoint(client):
    response = client.get("/api/v1/quality/overview")
    assert response.status_code == 200
    data = response.json()

    assert "total_products" in data
    assert "commerce_ready_products" in data
    assert "average_quality_score" in data
    assert "evidence_coverage_rate" in data
    assert "quality_defects" in data
    assert len(data["quality_defects"]) >= 3
