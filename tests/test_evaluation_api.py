"""
Test Suite for REST API v1 Evaluation Endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)


def test_evaluation_api_endpoints():
    # 1. POST /api/v1/evaluations/run
    run_resp = client.post("/api/v1/evaluations/run", json={
        "dataset_name": "Industrial Benchmark v1",
        "model_name": "llama3.2:3b"
    })
    assert run_resp.status_code == 200
    data = run_resp.json()
    eval_id = data["evaluation_id"]
    assert eval_id.startswith("eval_")
    assert data["quality_gate_status"] in ["PASS", "FAIL"]
    assert data["total_products"] == 10

    # 2. GET /api/v1/evaluations
    list_resp = client.get("/api/v1/evaluations")
    assert list_resp.status_code == 200
    runs = list_resp.json()["evaluations"]
    assert len(runs) >= 1

    # 3. GET /api/v1/evaluations/{id}
    single_resp = client.get(f"/api/v1/evaluations/{eval_id}")
    assert single_resp.status_code == 200
    assert single_resp.json()["evaluation_id"] == eval_id

    # 4. GET /api/v1/evaluations/{id}/metrics
    metrics_resp = client.get(f"/api/v1/evaluations/{eval_id}/metrics")
    assert metrics_resp.status_code == 200
    assert len(metrics_resp.json()["metrics"]) >= 5

    # 5. GET /api/v1/evaluations/{id}/products
    prods_resp = client.get(f"/api/v1/evaluations/{eval_id}/products")
    assert prods_resp.status_code == 200
    assert len(prods_resp.json()["products"]) == 10

    # 6. GET /api/v1/evaluations/{id}/report
    report_resp = client.get(f"/api/v1/evaluations/{eval_id}/report")
    assert report_resp.status_code == 200
    assert "PRODUCTIQ AI EVALUATION REPORT" in report_resp.json()["report_text"]

    # 7. GET /api/v1/evaluations/{id}/confusion-matrix
    cm_resp = client.get(f"/api/v1/evaluations/{eval_id}/confusion-matrix")
    assert cm_resp.status_code == 200
    assert "confusion_matrix" in cm_resp.json()
    assert "calibration_buckets" in cm_resp.json()

    # 8. GET /api/v1/evaluations/baseline/compare
    base_resp = client.get("/api/v1/evaluations/baseline/compare")
    assert base_resp.status_code == 200
    assert "comparison" in base_resp.json()
