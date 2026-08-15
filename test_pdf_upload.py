"""
Automated Test Suite for Robust PDF Upload & State Management in ProductIQ AI (Phase 11 Fix).
Tests non-flickering upload handler, persistent storage copying, sample button isolation,
dynamic file switching, state reset, and LLM inference isolation during upload.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from backend.pipeline import process_product_intelligence
from app import (
    demo, handle_pdf_upload, handle_pdf_clear, clear_pdf_ui_handler,
    load_sample_datasheet, analyze_product_ui, format_evidence_card
)


def test_pdf_upload_robustness():
    print("==================================================")
    print("PRODUCTIQ AI -- PDF UPLOAD ROBUSTNESS TEST SUITE")
    print("==================================================")

    pdf_sensor = os.path.join("data", "Test_Temperature_Sensor.pdf")
    pdf_valve = os.path.join("data", "Test_Pressure_Valve.pdf")
    pdf_bearing = os.path.join("data", "Test_Industrial_Bearing.pdf")
    pdf_sample = os.path.join("data", "ProductIQ_Test_Industrial_Pneumatic_Cylinder.pdf")

    # TEST 1: Application imports successfully
    print("\n--- 1. Testing Application Import ---")
    assert demo is not None, "Gradio demo object failed to import"
    print("[PASS] Application imported successfully.")

    # TEST 2 & 4 & 5 & 6: Upload handler accepts PDF, copies to uploads/, persistent path exists, filename preserved
    print("\n--- 2. Testing Upload Handler & Persistent Storage Copy ---")
    upload_res = handle_pdf_upload(pdf_sensor)
    pdf_state_path = upload_res[0]

    assert pdf_state_path is not None, "pdf_state_path must not be None"
    assert os.path.exists(pdf_state_path), f"Persistent path does not exist: {pdf_state_path}"
    assert "uploads" in pdf_state_path.lower(), f"Expected uploads directory, got: {pdf_state_path}"
    assert "Test_Temperature_Sensor.pdf" in pdf_state_path, "Original filename not preserved in persistent path"
    print(f"[PASS] PDF uploaded & copied to persistent storage: '{pdf_state_path}'.")

    # TEST 3: Upload handler rejects non-PDF
    print("\n--- 3. Testing Rejection of Invalid Non-PDF Files ---")
    invalid_file = os.path.join("data", "invalid_sample.exe")
    with open(invalid_file, "w") as f:
        f.write("binary data")
    try:
        upload_err_res = handle_pdf_upload(invalid_file)
        assert upload_err_res[0] is None, "pdf_state_path should be None for invalid unsupported file"
        assert "Upload Error" in upload_err_res[1] or "Unsupported" in upload_err_res[1], "Missing invalid format error banner"
        print("[PASS] Unsupported file type correctly rejected with friendly alert.")
    finally:
        if os.path.exists(invalid_file):
            os.remove(invalid_file)

    # TEST 7: Uploading Temperature Sensor does not produce pneumatic cylinder filename
    print("\n--- 4. Testing Filename Isolation ---")
    assert "pneumatic" not in pdf_state_path.lower(), "Pneumatic cylinder filename leaked into temperature sensor upload!"
    print("[PASS] Filename isolation verified.")

    # TEST 8: Uploading Pressure Valve replaces previous selected file
    print("\n--- 5. Testing Multiple File Switching (Sensor -> Valve) ---")
    valve_upload_res = handle_pdf_upload(pdf_valve)
    valve_state_path = valve_upload_res[0]

    assert valve_state_path is not None, "Valve pdf_state_path must not be None"
    assert "Test_Pressure_Valve.pdf" in valve_state_path, "Valve filename missing"
    assert valve_state_path != pdf_state_path, "Valve path did not replace sensor path"
    print(f"[PASS] File switching verified: '{valve_state_path}'.")

    # TEST 9: Sample PDF is NOT automatically selected on startup
    print("\n--- 6. Testing Application Startup Isolation ---")
    initial_ui = clear_pdf_ui_handler()
    assert initial_ui[0] is None, "pdf_state must be None on app startup"
    print("[PASS] Application startup contains no automatic sample PDF selection.")

    # TEST 10: Explicit sample button still selects sample PDF
    print("\n--- 7. Testing Explicit Sample Button ---")
    sample_res = load_sample_datasheet()
    assert sample_res[0] == pdf_sample, "Sample input path mismatch"
    assert "sample_pneumatic_cylinder.pdf" in sample_res[1], "Sample pdf_state path mismatch"
    assert sample_res[2] == "Acme Industrial Systems Pvt. Ltd.", "Sample manufacturer mismatch"
    print("[PASS] Explicit sample button loads sample PDF and metadata.")

    # TEST 11: Analyze uses currently selected PDF
    print("\n--- 8. Testing Analyze with Selected PDF State ---")
    # Analyze Temperature Sensor via pdf_state_path
    res_analysis = analyze_product_ui(pdf_state_path, "", "", "", "", "")
    rec = res_analysis[10]
    prod_name = rec["product"]["product_name"]
    code = rec["product"]["product_code"]

    print(f"Extracted Product: {prod_name} | Code: {code}")
    assert "sensor" in prod_name.lower() or "temperature" in prod_name.lower(), f"Expected sensor product, got: {prod_name}"

    ev_card = format_evidence_card(rec["specifications"][0]["name"], rec)
    assert "Test_Temperature_Sensor.pdf" in ev_card, f"Evidence source file mismatch! Got: {ev_card}"
    print("[PASS] Analyze button executed pipeline on currently selected PDF state.")

    # TEST 12: Clearing selection sets state to None
    print("\n--- 9. Testing Clear Action ---")
    cleared = handle_pdf_clear()
    assert cleared[0] is None, "pdf_state must be None after clear"
    assert cleared[1] == "", "Status output must be empty"
    print("[PASS] Clear action resets state to None.")

    # TEST 13 & 14 & 15: Fast upload handler execution (No LLM inference, no recursive outputs)
    print("\n--- 10. Testing Fast Upload Execution & Inference Isolation ---")
    t0 = time.time()
    fast_res = handle_pdf_upload(pdf_bearing)
    duration = time.time() - t0
    assert duration < 1.0, f"Upload handler took too long ({duration:.2f}s)! Must not run LLM during upload."
    assert "Test_Industrial_Bearing.pdf" in fast_res[0], "Bearing upload failed"
    print(f"[PASS] Upload handler executed in {duration:.3f}s without running LLM inference.")

    print("\n==================================================")
    print("ALL 10 UPLOAD ROBUSTNESS TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_pdf_upload_robustness()
    sys.exit(0 if success else 1)
