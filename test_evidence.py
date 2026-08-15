"""
Automated Test Suite for ProductIQ AI Evidence Isolation & Confidence Scoring.
Tests verbatim quote isolation, page attribution, confidence computation (0-100%), and anti-hallucination.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from backend.evidence import isolate_evidence
from backend.confidence import calculate_attribute_confidence


def test_evidence_suite():
    print("==================================================")
    print("PRODUCTIQ AI -- EVIDENCE & CONFIDENCE TEST SUITE")
    print("==================================================")

    # 1. Test Evidence Isolation (Verbatim Match & Page Attribution)
    print("\n--- 1. Testing Verbatim Evidence Isolation ---")
    raw_pages = [
        {
            "filename": "Test_Temperature_Sensor.pdf",
            "page": 1,
            "text": "INDUSTRIAL TEMPERATURE SENSORS\nModel: TS-100\nOperating Range: -50 to 200 °C\nSupply Voltage: 24 V DC\nAccuracy: ±0.5 °C"
        },
        {
            "filename": "Test_Temperature_Sensor.pdf",
            "page": 2,
            "text": "MOUNTING & DIMENSIONS\nThread Size: G1/2\nProbe Length: 100 mm\nBody Material: 316 Stainless Steel"
        }
    ]

    # Match attribute on page 1
    matched_page, snippet, score = isolate_evidence("Supply Voltage", "24", "V DC", raw_pages)
    assert matched_page == 1, f"Expected page 1, got {matched_page}"
    assert "Supply Voltage: 24 V DC" in snippet, f"Evidence snippet mismatch: '{snippet}'"
    assert score > 0.8, f"Expected high evidence match score, got {score}"
    print(f"[PASS] Page 1 attribute matched: page={matched_page}, snippet='{snippet}', score={score:.2f}")

    # Match attribute on page 2
    matched_page2, snippet2, score2 = isolate_evidence("Probe Length", "100", "mm", raw_pages)
    assert matched_page2 == 2, f"Expected page 2, got {matched_page2}"
    assert "Probe Length: 100 mm" in snippet2, f"Evidence snippet mismatch: '{snippet2}'"
    print(f"[PASS] Page 2 attribute matched: page={matched_page2}, snippet='{snippet2}', score={score2:.2f}")

    # 2. Test Confidence Score Calculation
    print("\n--- 2. Testing Confidence Score Computation (0-100%) ---")
    high_conf = calculate_attribute_confidence(
        val_str="100", unit_str="mm", page_num=1,
        evidence_snippet="Probe Length: 100 mm", evidence_score=0.95
    )
    assert high_conf >= 90.0, f"Expected high confidence >=90, got {high_conf}"
    print(f"[PASS] Valid evidence confidence: {high_conf}%")

    low_conf = calculate_attribute_confidence(
        val_str="Unknown", unit_str=None, page_num=None,
        evidence_snippet="", evidence_score=0.0
    )
    assert low_conf < 50.0, f"Expected low confidence <50 for missing evidence, got {low_conf}"
    print(f"[PASS] Missing evidence confidence: {low_conf}%")

    # 3. Test Anti-Hallucination Guard (Unmentioned Attribute)
    print("\n--- 3. Testing Anti-Hallucination Evidence Fallback ---")
    unmatched_page, unmatched_snippet, unmatched_score = isolate_evidence(
        "Warranty Period", "5 years", None, raw_pages
    )
    assert unmatched_score < 0.4, "Hallucinated value should have low evidence match score"
    print(f"[PASS] Unmentioned attribute evidence isolated correctly (score={unmatched_score:.2f}).")

    print("\n==================================================")
    print("ALL EVIDENCE & CONFIDENCE TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_evidence_suite()
    sys.exit(0 if success else 1)
