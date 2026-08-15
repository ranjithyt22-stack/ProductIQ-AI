"""
Automated Test Suite for Gradio Event Architecture & Static Verification (Phase 11 Bug Fix).
Verifies component definitions, event output counts, execution speed, LLM inference isolation,
and state management without starting server process loops.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from app import (
    demo, handle_pdf_upload, handle_pdf_clear,
    load_sample_datasheet, analyze_product_ui, format_evidence_card
)


def test_gradio_event_architecture():
    print("==================================================")
    print("PRODUCTIQ AI -- GRADIO EVENT ARCHITECTURE TEST SUITE")
    print("==================================================")

    pdf_sensor = os.path.join("data", "Test_Temperature_Sensor.pdf")
    pdf_valve = os.path.join("data", "Test_Pressure_Valve.pdf")

    assert os.path.exists(pdf_sensor), "Test_Temperature_Sensor.pdf missing!"
    assert os.path.exists(pdf_valve), "Test_Pressure_Valve.pdf missing!"

    # 1. Application imports cleanly
    print("\n--- 1. Testing Clean Application Import ---")
    assert demo is not None, "Gradio demo failed to load"
    print("[PASS] Gradio app loaded cleanly without infinite loops.")

    # 2. Upload Handler Output Count & Inference Isolation
    print("\n--- 2. Testing Upload Handler Output Count & Inference Isolation ---")
    t0 = time.time()
    upload_res = handle_pdf_upload(pdf_sensor)
    duration = time.time() - t0

    assert isinstance(upload_res, tuple), "Upload handler must return a tuple"
    assert len(upload_res) == 2, f"Upload handler MUST return exactly 2 outputs (pdf_state, status_output), got {len(upload_res)}"
    persistent_path, status_html = upload_res

    assert persistent_path is not None, "Persistent path is None"
    assert os.path.exists(persistent_path), f"Persistent path does not exist: {persistent_path}"
    assert duration < 0.1, f"Upload handler took {duration:.3f}s! Must complete <0.1s without running LLM."
    print(f"[PASS] Upload handler returned 2 outputs in {duration:.3f}s. Persistent path: '{persistent_path}'.")

    # 3. Clear Handler Output Count
    print("\n--- 3. Testing Clear Handler Output Count ---")
    clear_res = handle_pdf_clear()
    assert isinstance(clear_res, tuple), "Clear handler must return a tuple"
    assert len(clear_res) == 2, f"Clear handler MUST return exactly 2 outputs, got {len(clear_res)}"
    assert clear_res[0] is None, "pdf_state must be None after clear"
    assert clear_res[1] == "", "status_output must be empty after clear"
    print("[PASS] Clear handler returned exactly 2 outputs (None, '').")

    # 4. Invalid File Handling
    print("\n--- 4. Testing Invalid File Handling ---")
    invalid_file = os.path.join("data", "invalid_sample.exe")
    with open(invalid_file, "w") as f:
        f.write("binary data")
    try:
        invalid_res = handle_pdf_upload(invalid_file)
        assert invalid_res[0] is None, "pdf_state should be None for unsupported file format"
        assert "Upload Error" in invalid_res[1] or "Unsupported" in invalid_res[1], "Missing error message"
        print("[PASS] Unsupported file format rejected gracefully with 2 outputs.")
    finally:
        if os.path.exists(invalid_file):
            os.remove(invalid_file)

    # 5. Multiple File Upload Switching
    print("\n--- 5. Testing File Switching (Sensor -> Valve) ---")
    valve_res = handle_pdf_upload(pdf_valve)
    valve_path = valve_res[0]
    assert valve_path is not None, "Valve path is None"
    assert "Test_Pressure_Valve.pdf" in valve_path, "Valve filename missing"
    assert valve_path != persistent_path, "New upload path must replace previous upload path"
    print(f"[PASS] File switching verified: '{valve_path}'.")

    # 6. Analyze Button Execution
    print("\n--- 6. Testing Analyze Button Execution ---")
    analysis_res = analyze_product_ui(persistent_path, "", "", "", "", "")
    assert len(analysis_res) == 11, f"Analyze handler must return 11 outputs, got {len(analysis_res)}"
    rec = analysis_res[10]
    prod_name = rec["product"]["product_name"]
    print(f"Extracted Product: {prod_name}")
    assert "sensor" in prod_name.lower() or "temperature" in prod_name.lower(), f"Unexpected product: {prod_name}"
    print("[PASS] Analyze button executed pipeline cleanly on persistent pdf_state.")

    # 7. Analyze Without PDF State Error Handling
    print("\n--- 7. Testing Analyze Without PDF State ---")
    err_res = analyze_product_ui(None, "", "", "", "", "")
    assert "Please upload" in err_res[0], "Missing input required error mismatch"

    print("[PASS] Analyzing without PDF state returns friendly error message.")

    print("\n==================================================")
    print("ALL GRADIO EVENT ARCHITECTURE TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_gradio_event_architecture()
    sys.exit(0 if success else 1)
