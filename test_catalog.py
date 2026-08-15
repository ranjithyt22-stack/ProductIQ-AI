"""
Automated Test Suite for ProductIQ AI Scalable Catalog Engine (Phase 10).
Tests CSV parsing, product ID generation, batch orchestration, fault tolerance,
metrics aggregation, exports, search/filtering, and edge cases.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))

from backend.models import (
    CatalogProduct, CatalogResult, CatalogProcessingStatus, ProductInfo,
    SpecificationAttribute, ValidationResult, ProductQualityScore, ProductIntelligenceRecord
)
from backend.catalog import (
    parse_catalog_csv, aggregate_catalog_metrics, process_catalog_batch,
    export_catalog_csv, export_catalog_json
)
from app import filter_catalog_table_ui


def create_mock_pipeline_fn(fail_on_index: int = -1):
    """Factory creating deterministic pipeline function for fast unit testing."""
    idx = [0]

    def mock_pipeline(pdf_path, manufacturer, product_name, product_code, description, product_url):
        current_i = idx[0]
        idx[0] += 1

        if current_i == fail_on_index:
            return None, "Simulated extraction failure for product."

        p_info = ProductInfo(
            product_name=product_name or f"Mock Product {current_i+1}",
            manufacturer=manufacturer or "Acme Corp",
            product_code=product_code or f"MP-{current_i+1:03d}",
            category="Industrial Component",
            description=description or "Synthetic test item."
        )

        specs = [
            SpecificationAttribute(name="Bore", value="50", unit="mm", page=1, evidence="Bore 50 mm", confidence=95.0),
            SpecificationAttribute(name="Pressure", value="1 to 10", unit="bar", page=1, evidence="Pressure 1 to 10 bar", confidence=95.0)
        ]

        vals = [
            ValidationResult(rule="Required Check", status="PASS", severity="INFO", message="Product Name identified.", field="product_name"),
            ValidationResult(rule="Unit Check", status="PASS", severity="INFO", message="Unit mm valid.", field="Bore")
        ]

        qs = ProductQualityScore(
            overall_score=95,
            completeness=100,
            extraction_quality=95,
            validation_quality=100,
            evidence_coverage=100,
            consistency=100,
            status_category="READY FOR COMMERCE"
        )

        record = ProductIntelligenceRecord(
            product_id=f"PIQ-{current_i+1:06d}",
            product=p_info,
            specifications=specs,
            validation=vals,
            quality_score=qs,
            review_status="ai_extracted"
        )

        return record, ""

    return mock_pipeline


def test_catalog_engine():
    print("==================================================")
    print("PRODUCTIQ AI -- CATALOG ENGINE AUTOMATED TEST SUITE")
    print("==================================================")

    # Test 1: CSV Parsing & Product ID Generation
    print("\n--- 1. Testing CSV Parsing & Product ID Generation ---")
    sample_csv_path = os.path.join("data", "sample_catalog.csv")
    assert os.path.exists(sample_csv_path), "sample_catalog.csv missing!"

    parsed_items = parse_catalog_csv(sample_csv_path)
    assert len(parsed_items) >= 5, f"Expected at least 5 items, got {len(parsed_items)}"
    assert parsed_items[0]["product_id"] == "PIQ-000001", f"Expected PIQ-000001, got {parsed_items[0]['product_id']}"
    assert parsed_items[1]["product_id"] == "PIQ-000002", f"Expected PIQ-000002, got {parsed_items[1]['product_id']}"
    print(f"[PASS] CSV parsed successfully ({len(parsed_items)} items). Dynamic IDs generated.")

    # Test 2: Batch Processing & Fault Tolerance (Product 2 failure should NOT stop batch)
    print("\n--- 2. Testing Batch Processing & Fault Tolerance ---")
    mock_pipeline = create_mock_pipeline_fn(fail_on_index=1)  # Fail item #2
    catalog_result = process_catalog_batch(parsed_items, custom_pipeline_fn=mock_pipeline)

    assert catalog_result.total_products == len(parsed_items), "Total products mismatch"
    assert catalog_result.processed_products == len(parsed_items) - 1, "Processed count mismatch"
    assert catalog_result.failed_products == 1, "Failed count mismatch"
    assert catalog_result.products[1].status == CatalogProcessingStatus.FAILED, "Item 2 should be FAILED"
    assert "Simulated extraction failure" in catalog_result.products[1].error_message, "Error message missing on item 2"
    assert catalog_result.products[0].status == CatalogProcessingStatus.COMPLETED, "Item 1 should be COMPLETED"
    assert catalog_result.products[2].status == CatalogProcessingStatus.COMPLETED, "Item 3 should be COMPLETED (Batch continued!)"
    print("[PASS] Fault tolerance verified: Single product failure recorded status=FAILED without stopping batch!")

    # Test 3: Quality Metrics & Aggregation
    print("\n--- 3. Testing Quality Metrics Aggregation ---")
    assert catalog_result.average_quality_score > 0, "Average quality score must be positive"
    assert catalog_result.average_evidence_coverage > 0, "Evidence coverage must be positive"
    assert catalog_result.validation_pass_rate == 100.0, "Validation pass rate calculation mismatch"
    print(f"[PASS] Aggregated metrics: Avg Score={catalog_result.average_quality_score}, Evidence Cov={catalog_result.average_evidence_coverage}%, Val Pass={catalog_result.validation_pass_rate}%")

    # Test 4: Catalog Exports (CSV & JSON)
    print("\n--- 4. Testing Catalog Exports ---")
    cat_csv = export_catalog_csv(catalog_result)
    cat_json = export_catalog_json(catalog_result)

    assert "product_id,product_name" in cat_csv, "Catalog CSV header missing"
    assert "PIQ-000001" in cat_csv, "Product ID missing in CSV export"
    assert "PIQ-000002" in cat_csv, "Failed Product ID missing in CSV export"

    json_parsed = json.loads(cat_json)
    assert json_parsed["total_products"] == len(parsed_items), "JSON total_products mismatch"
    assert len(json_parsed["products"]) == len(parsed_items), "JSON products array length mismatch"
    print("[PASS] Catalog CSV and JSON exports verified cleanly.")

    # Test 5: Catalog Search & Filter
    print("\n--- 5. Testing Catalog Table Search & Filtering ---")
    cat_dict = catalog_result.to_dict()

    df_all = filter_catalog_table_ui("", "All", "All", cat_dict)
    assert len(df_all) == len(parsed_items), f"Expected {len(parsed_items)} rows, got {len(df_all)}"

    df_failed = filter_catalog_table_ui("", "All", CatalogProcessingStatus.FAILED, cat_dict)
    assert len(df_failed) == 1, f"Expected 1 failed row, got {len(df_failed)}"

    df_search = filter_catalog_table_ui("PV-200", "All", "All", cat_dict)
    assert len(df_search) >= 1, "Search filter failed for code PV-200"
    print("[PASS] Table search & readiness/status filters verified.")

    # Test 6: Edge Cases (Empty CSV & Invalid CSV)
    print("\n--- 6. Testing Edge Cases (Empty & Invalid CSV) ---")
    empty_items = parse_catalog_csv("")
    assert empty_items == [], "Empty CSV should return empty list"

    invalid_items = parse_catalog_csv("invalid,header,only\n")
    assert isinstance(invalid_items, list), "Invalid CSV should return list"
    print("[PASS] Edge cases handled gracefully.")

    print("\n==================================================")
    print("ALL 15 CATALOG ENGINE AUTOMATED TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_catalog_engine()
    sys.exit(0 if success else 1)
