"""
Automated Test Suite for ProductIQ AI End-to-End Workflow (Section 40 Acceptance Tests).
Executes the exact 10-step hackathon demo flow programmatically.
Uses mocked LLM extraction to enable reliable CI testing without Ollama.
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api import app as fastapi_app
from backend.ingestion import ingest_sources
from backend.ingestion.models import SourceDocument
from backend.pipeline import process_product_intelligence
from app import (
    demo, handle_pdf_upload, handle_pdf_clear, analyze_product_ui,
    analyze_catalog_ui, format_evidence_card
)

client = TestClient(fastapi_app)

# Deterministic mock LLM responses keyed by detected product keyword
def make_mock_extraction(product_name, manufacturer, product_code, category, description, specs=None):
    return {
        "product": {
            "product_name": product_name,
            "manufacturer": manufacturer,
            "product_code": product_code,
            "category": category,
            "description": description,
        },
        "specifications": specs or [
            {"name": "Operating Temperature", "value": "0 to 85", "unit": "degC", "page": 1, "evidence": "Operating temperature range: 0 to 85 degC"},
        ],
        "applications": ["Industrial automation", "Process control"],
        "keywords": [product_name, category],
        "enrichment": {
            "search_terms": [product_name],
            "category_path": ["Industrial Equipment", category],
            "suggested_applications": ["Industrial automation"]
        }
    }

SENSOR_MOCK = make_mock_extraction(
    "Industrial Temperature Sensor TS-200",
    "SensorTech Industries",
    "TS-200",
    "Temperature Sensor",
    "High-precision industrial temperature sensor for process control applications.",
    [{"name": "Measuring Range", "value": "-50 to 200", "unit": "degC", "page": 1, "evidence": "Measuring range: -50 to 200 degC"}]
)

VALVE_MOCK = make_mock_extraction(
    "High-Flow Solenoid Pressure Valve PV-200",
    "FlowControl Tech Inc",
    "PV-200",
    "Pressure Valve",
    "2-way solenoid operated directional control pressure valve for industrial hydraulic systems.",
    [{"name": "Max Operating Pressure", "value": "400", "unit": "bar", "page": 1, "evidence": "Maximum operating pressure: 400 bar"}]
)

MULTI_MOCK = make_mock_extraction(
    "Industrial Temperature Sensor TS-200",
    "SensorTech Industries",
    "TS-200",
    "Temperature Sensor",
    "High-precision industrial temperature sensor for process control applications.",
    [{"name": "Measuring Range", "value": "-50 to 200", "unit": "degC", "page": 1, "evidence": "Measuring range: -50 to 200 degC"}]
)


def _make_ollama_side_effect():
    """Returns a side_effect function that returns different mock data based on call count."""
    call_count = [0]
    mocks = [SENSOR_MOCK, VALVE_MOCK, MULTI_MOCK]
    def side_effect(doc_text, user_ctx=None):
        idx = min(call_count[0], len(mocks) - 1)
        call_count[0] += 1
        return mocks[idx], ""
    return side_effect


def test_end_to_end_suite():
    print("==================================================")
    print("PRODUCTIQ AI -- END-TO-END HACKATHON WORKFLOW TEST")
    print("==================================================")

    pdf_sensor = os.path.join("data", "Test_Temperature_Sensor.pdf")
    pdf_valve = os.path.join("data", "Test_Pressure_Valve.pdf")

    assert os.path.exists(pdf_sensor), "Test_Temperature_Sensor.pdf missing!"
    assert os.path.exists(pdf_valve), "Test_Pressure_Valve.pdf missing!"

    # Use a single mock for the Ollama LLM call across all steps to remove Ollama dependency
    ollama_side_effect = _make_ollama_side_effect()

    with patch("backend.extraction.call_ollama_structured_extraction", side_effect=ollama_side_effect):
        # STEP 1: App startup verification (No processing, no sample loaded automatically)
        print("\n--- STEP 1: Application Startup Verification ---")
        assert demo is not None, "Gradio demo failed to initialize"
        cleared = handle_pdf_clear()
        assert cleared[0] is None, "pdf_state must be None on startup"
        print("[PASS] Step 1: App initialized without running LLM or loading sample data.")

        # STEP 2: Upload Test_Temperature_Sensor.pdf
        print("\n--- STEP 2: Upload Temperature Sensor PDF ---")
        sensor_res = handle_pdf_upload(pdf_sensor)
        sensor_state_path = sensor_res[0]
        assert sensor_state_path is not None, "Temperature sensor pdf_state_path is None"
        assert "Test_Temperature_Sensor.pdf" in sensor_state_path, "Filename mismatch"
        print(f"[PASS] Step 2: Temperature Sensor uploaded without automatic analysis: '{sensor_state_path}'.")

        # STEP 3: Click Analyze (Single Product) -- uses SENSOR_MOCK
        print("\n--- STEP 3: Analyze Temperature Sensor ---")
        analysis_sensor = analyze_product_ui(sensor_state_path, "", "", "", "", "")
        sensor_rec = analysis_sensor[10]
        assert sensor_rec is not None, "Sensor analysis returned no record dict"
        s_name = sensor_rec["product"]["product_name"]
        print(f"Extracted Product Name: '{s_name}'")
        assert s_name is not None, f"Product name is None after sensor analysis"
        assert "sensor" in s_name.lower() or "temperature" in s_name.lower(), f"Expected sensor, got: {s_name}"
        print("[PASS] Step 3: Single product analysis returned Industrial Temperature Sensor.")

        # STEP 4: Clear Selection
        print("\n--- STEP 4: Clear Upload Selection ---")
        clear_res = handle_pdf_clear()
        assert clear_res[0] is None, "pdf_state should be None after clear"
        print("[PASS] Step 4: Clear selection reset state cleanly.")

        # STEP 5: Upload Test_Pressure_Valve.pdf
        print("\n--- STEP 5: Upload Pressure Valve PDF ---")
        valve_res = handle_pdf_upload(pdf_valve)
        valve_state_path = valve_res[0]
        assert valve_state_path is not None, "Valve state path is None"
        assert "Test_Pressure_Valve.pdf" in valve_state_path, "Valve filename mismatch"
        print(f"[PASS] Step 5: Pressure Valve uploaded: '{valve_state_path}'.")

        # STEP 6: Analyze Pressure Valve -- uses VALVE_MOCK; result must NOT contain sensor name
        print("\n--- STEP 6: Analyze Pressure Valve ---")
        analysis_valve = analyze_product_ui(valve_state_path, "", "", "", "", "")
        valve_rec = analysis_valve[10]
        assert valve_rec is not None, "Valve analysis returned no record dict"
        v_name = valve_rec["product"]["product_name"]
        print(f"Extracted Product Name: '{v_name}'")
        assert v_name is not None, f"Product name is None after valve analysis"
        assert "valve" in v_name.lower() or "pressure" in v_name.lower(), f"Expected valve, got: {v_name}"
        # Isolation check: valve result must NOT contain Temperature Sensor identity
        assert "temperature sensor" not in v_name.lower(), f"Sensor data leaked into valve result: '{v_name}'"
        print("[PASS] Step 6: Single product analysis returned Industrial Pressure Valve.")
        print("[PASS] Step 6: Isolation verified - no Temperature Sensor data leaked into Valve result.")

        # STEP 7: Enter Web URL
        print("\n--- STEP 7: Ingest Product URL ---")
        url_res = client.post("/analyze/url", json={"url": "https://example.com"})
        assert url_res.status_code in [200, 400], f"Unexpected status: {url_res.status_code}"
        print(f"[PASS] Step 7: URL ingestion handled cleanly (HTTP {url_res.status_code}).")

        # STEP 8: Upload PDF + Text Together (Multi-Source Analysis)
        print("\n--- STEP 8: Multi-Source Analysis (PDF + Supplementary Text) ---")
        docs = ingest_sources(
            files=[sensor_state_path],
            text="Supplementary notes: Precision industrial sensor."
        )
        multi_rec, err = process_product_intelligence(source_documents=docs)
        assert err == "", f"Multi-source analysis error: {err}"
        assert multi_rec is not None, "Multi-source record is None"
        assert len(multi_rec.raw_sources) >= 2, "Expected at least 2 raw sources in multi-source record"
        print(f"[PASS] Step 8: Multi-source analysis succeeded with {len(multi_rec.raw_sources)} recorded sources.")

    # STEP 9: Catalog Engine Processing (With fast mock for external web pages)
    print("\n--- STEP 9: Catalog Engine Batch Analysis ---")
    sample_csv = os.path.join("data", "sample_catalog.csv")
    mock_docs = [SourceDocument(
        source_id="web_mock_1",
        source_type="url",
        source_name="Mock Page",
        content="Product webpage content for testing."
    )]

    with patch("backend.pipeline.ingest_sources", return_value=mock_docs):
        cat_res = analyze_catalog_ui(sample_csv, None)

    assert cat_res[7] is not None, "Catalog state dict is None"
    total_cat = cat_res[7].get("total_products", 0)
    assert total_cat >= 5, f"Expected >=5 catalog items, got {total_cat}"
    print(f"[PASS] Step 9: Catalog Engine processed {total_cat} catalog products.")

    # STEP 10: REST API Documentation Health Check
    print("\n--- STEP 10: OpenAPI Documentation & REST API Check ---")
    health_res = client.get("/health")
    assert health_res.status_code == 200, "API health check failed"
    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200, "OpenAPI documentation endpoint failed"
    print(f"[PASS] Step 10: REST API & OpenAPI docs working cleanly (status={health_res.json()['status']}).")

    print("\n==================================================")
    print("ALL 10 END-TO-END HACKATHON WORKFLOW STEPS PASSED PERFECTLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_end_to_end_suite()
    sys.exit(0 if success else 1)
