"""
Automated Test Suite for ProductIQ AI REST API.
Tests /health, /analyze, /validate, /enrich, /catalog/analyze, /catalog/{catalog_id},
schema validation (422), 404 handling, and v1 Persistence, Versioning & Lineage API routes.
"""

import sys
import os
import json
from unittest.mock import patch

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api import app, CATALOG_STORE
from backend.models import CatalogResult, CatalogProcessingStatus, ProductIntelligenceRecord, ProductInfo, SpecificationAttribute
from backend.ingestion.models import SourceDocument
from backend.database.connection import get_db_context
from backend.database.repositories import ProductRepository

client = TestClient(app)


def test_api_endpoints():
    print("==================================================")
    print("PRODUCTIQ AI -- REST API AUTOMATED TEST SUITE")
    print("==================================================")

    # 1. GET /health
    print("\n--- 1. Testing GET /health ---")
    res = client.get("/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    body = res.json()
    assert body["status"] in ["ok", "degraded"], "Invalid health status"
    assert "ollama" in body, "Health response missing ollama field"
    assert "database" in body, "Health response missing database field"
    print(f"[PASS] GET /health returned status={body['status']}, ollama={body['ollama']}, db={body['database']}")

    # 2. Invalid Request Schema (HTTP 422)
    print("\n--- 2. Testing Invalid Request Schema (HTTP 422) ---")
    res_bad = client.post("/validate", json={"invalid": "payload"})
    assert res_bad.status_code == 422, f"Expected 422, got {res_bad.status_code}"
    print("[PASS] Invalid schema correctly rejected with HTTP 422.")

    # 3. POST /validate
    print("\n--- 3. Testing POST /validate ---")
    val_payload = {
        "product": {
            "product_name": "Pneumatic Cylinder PC-50-100",
            "manufacturer": "Acme Industrial Systems Pvt. Ltd.",
            "product_code": "PC-50-100",
            "category": "Pneumatic Cylinder"
        },
        "specifications": [
            {"name": "Bore Diameter", "value": "50", "unit": "mm"},
            {"name": "Operating Pressure", "value": "1 to 10", "unit": "bar"}
        ]
    }
    res_val = client.post("/validate", json=val_payload)
    assert res_val.status_code == 200, f"Expected 200, got {res_val.status_code}"
    val_results = res_val.json()
    assert isinstance(val_results, list), "Expected list of validation results"
    assert len(val_results) > 0, "Validation results empty"
    print(f"[PASS] POST /validate returned {len(val_results)} validation check items.")

    # 4. POST /enrich
    print("\n--- 4. Testing POST /enrich ---")
    enrich_payload = {
        "product": {
            "product_name": "Pneumatic Cylinder PC-50-100",
            "manufacturer": "Acme Industrial Systems Pvt. Ltd.",
            "category": "Pneumatic Cylinder"
        },
        "specifications": [
            {"name": "Bore Diameter", "value": "50", "unit": "mm"}
        ]
    }
    res_enrich = client.post("/enrich", json=enrich_payload)
    assert res_enrich.status_code == 200, f"Expected 200, got {res_enrich.status_code}"
    enrich_dict = res_enrich.json()
    assert "category_path" in enrich_dict, "Missing category_path in enrichment"
    assert "search_terms" in enrich_dict, "Missing search_terms in enrichment"
    print("[PASS] POST /enrich returned valid taxonomy and search enrichment.")

    # 5. POST /catalog/analyze
    print("\n--- 5. Testing POST /catalog/analyze ---")
    sample_csv_path = os.path.join("data", "sample_catalog.csv")
    assert os.path.exists(sample_csv_path), "sample_catalog.csv missing!"

    mock_rec = ProductIntelligenceRecord(
        product_id="PIQ-000001",
        product=ProductInfo(product_name="Catalog Test Product", manufacturer="Test Mfr")
    )

    with patch("backend.catalog.process_product_intelligence", return_value=(mock_rec, None)):
        with open(sample_csv_path, "rb") as f:
            res_cat = client.post(
                "/catalog/analyze",
                files={"file": ("sample_catalog.csv", f, "text/csv")}
            )

    assert res_cat.status_code == 200, f"Expected 200, got {res_cat.status_code}"
    cat_body = res_cat.json()
    assert "catalog_id" in cat_body, "Catalog response missing catalog_id"
    assert cat_body["total_products"] >= 5, f"Expected >=5 products, got {cat_body['total_products']}"
    cat_id = cat_body["catalog_id"]
    print(f"[PASS] POST /catalog/analyze succeeded (catalog_id={cat_id}, total={cat_body['total_products']}).")

    # 6. GET /catalog/{catalog_id} (Success)
    print("\n--- 6. Testing GET /catalog/{catalog_id} (Success) ---")
    res_get_cat = client.get(f"/catalog/{cat_id}")
    assert res_get_cat.status_code == 200, f"Expected 200, got {res_get_cat.status_code}"
    assert res_get_cat.json()["catalog_id"] == cat_id
    print(f"[PASS] GET /catalog/{cat_id} successfully retrieved catalog record.")

    # 7. GET /catalog/{catalog_id} (404 Not Found)
    print("\n--- 7. Testing GET /catalog/{catalog_id} (404 Not Found) ---")
    res_404 = client.get("/catalog/NON_EXISTENT_CATALOG_999")
    assert res_404.status_code == 404, f"Expected 404, got {res_404.status_code}"
    print("[PASS] GET /catalog/NON_EXISTENT returned HTTP 404 Not Found.")

    # 8. v1 API: POST /api/v1/products & GET /api/v1/products
    print("\n--- 8. Testing v1 API: Products CRUD ---")
    test_pid = "API-V1-TEST-001"
    create_res = client.post("/api/v1/products", json={
        "product_id": test_pid,
        "product_name": "Optical Rotary Encoder RE-50",
        "manufacturer": "Kuebler Group",
        "product_code": "RE-50-1024",
        "category": "Encoders",
        "commerce_readiness": "READY FOR COMMERCE"
    })
    assert create_res.status_code == 200, f"Failed creating v1 product: {create_res.text}"
    print(f"[PASS] POST /api/v1/products created product '{test_pid}'.")

    list_res = client.get("/api/v1/products?search=Kuebler")
    assert list_res.status_code == 200
    assert list_res.json()["count"] >= 1
    print(f"[PASS] GET /api/v1/products listed products matching search.")

    # 9. v1 API: Data Lineage & Versions
    print("\n--- 9. Testing v1 API: Lineage & Versions ---")
    with get_db_context() as db:
        repo = ProductRepository(db)
        repo.save_full_record(
            ProductIntelligenceRecord(
                product_id=test_pid,
                product=ProductInfo(
                    product_name="Optical Rotary Encoder RE-50",
                    manufacturer="Kuebler Group",
                    product_code="RE-50-1024"
                ),
                specifications=[
                    SpecificationAttribute(name="Resolution", value="1024", unit="ppr", confidence=99.0, evidence="Resolution: 1024 ppr.")
                ]
            ),
            change_summary="Initial Calibration Record"
        )

    ver_res = client.get(f"/api/v1/products/{test_pid}/versions")
    assert ver_res.status_code == 200
    assert ver_res.json()["version_count"] >= 1
    print(f"[PASS] GET /api/v1/products/{test_pid}/versions returned versions.")

    lineage_res = client.get(f"/api/v1/products/{test_pid}/lineage")
    assert lineage_res.status_code == 200
    lineage_data = lineage_res.json()
    assert "lineage_items" in lineage_data
    assert len(lineage_data["lineage_items"]) >= 1
    print(f"[PASS] GET /api/v1/products/{test_pid}/lineage returned full data lineage graph.")

    print("\n==================================================")
    print("ALL REST API AUTOMATED TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
