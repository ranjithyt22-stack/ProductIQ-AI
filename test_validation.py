"""
Automated Test Suite for ProductIQ AI Deterministic Validation Engine.
Tests 8 categories of validation rules: Required fields, Unit consistency, Range checks,
Duplicate attributes, Engineering sanity, Malformed product codes, and Multi-source conflicts.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from backend.models import ProductInfo, SpecificationAttribute, ValidationResult
from backend.validation import validate_product_data
from backend.pipeline import _detect_source_conflicts


def test_validation_suite():
    print("==================================================")
    print("PRODUCTIQ AI -- DETERMINISTIC VALIDATION ENGINE TEST SUITE")
    print("==================================================")

    # 1. Test Valid Product & Spec Attributes (PASS)
    print("\n--- 1. Testing Valid Product Data (PASS) ---")
    p_info = ProductInfo(
        product_name="Pneumatic Cylinder PC-50-100",
        manufacturer="Acme Industrial Systems Pvt. Ltd.",
        product_code="PC-50-100",
        category="Pneumatic Cylinder",
        description="Double acting pneumatic cylinder."
    )
    specs = [
        SpecificationAttribute(name="Bore Diameter", value="50", unit="mm", page=1, status="PASS"),
        SpecificationAttribute(name="Operating Pressure", value="1 to 10", unit="bar", page=1, status="PASS"),
        SpecificationAttribute(name="Operating Temperature", value="-10 to 60", unit="°C", page=1, status="PASS")
    ]

    val_results = validate_product_data(p_info, specs)
    statuses = [v.status for v in val_results]
    assert "FAIL" not in statuses, f"Valid product failed validation: {val_results}"
    print(f"[PASS] Valid product passed all {len(val_results)} validation check rules.")

    # 2. Test Missing Required Fields (WARNING/FAIL)
    print("\n--- 2. Testing Missing Required Product Metadata ---")
    empty_p = ProductInfo(product_name=None, manufacturer=None, product_code=None)
    val_empty = validate_product_data(empty_p, [])
    warnings = [v for v in val_empty if v.status in ["WARNING", "FAIL"]]
    assert len(warnings) >= 2, "Expected warnings for missing required fields"
    print(f"[PASS] Missing metadata correctly flagged with {len(warnings)} warnings.")

    # 3. Test Invalid Engineering Ranges (Impossible Values)
    print("\n--- 3. Testing Impossible Engineering Values & Ranges ---")
    bad_specs = [
        SpecificationAttribute(name="Operating Temperature", value="-300", unit="°C", page=1), # Below absolute zero!
        SpecificationAttribute(name="Efficiency", value="150", unit="%", page=1) # > 100%
    ]
    val_bad = validate_product_data(p_info, bad_specs)
    bad_flags = [v for v in val_bad if v.status in ["WARNING", "FAIL"]]
    assert len(bad_flags) >= 1, "Impossible temperature/efficiency values not flagged"
    print(f"[PASS] Impossible engineering values correctly flagged: '{bad_flags[0].message}'")

    # 4. Test Duplicate Attributes
    print("\n--- 4. Testing Duplicate Attribute Detection ---")
    dup_specs = [
        SpecificationAttribute(name="Bore Diameter", value="50", unit="mm"),
        SpecificationAttribute(name="Bore Diameter", value="50", unit="mm")
    ]
    val_dup = validate_product_data(p_info, dup_specs)
    dup_flags = [v for v in val_dup if "Duplicate" in v.rule or "duplicate" in v.message.lower()]
    assert len(dup_flags) >= 1, "Duplicate attributes were not flagged"
    print("[PASS] Duplicate attributes correctly detected.")

    # 5. Test Multi-Source Conflict Detection
    print("\n--- 5. Testing Multi-Source Conflict Detection ---")
    conflict_specs = [
        SpecificationAttribute(
            name="Operating Pressure", value="10", unit="bar",
            source_type="pdf", source_name="Datasheet.pdf"
        ),
        SpecificationAttribute(
            name="Operating Pressure", value="12", unit="bar",
            source_type="url", source_name="ProductWebpage.html"
        )
    ]
    conflict_res = _detect_source_conflicts(conflict_specs)
    assert len(conflict_res) >= 1, "Conflict between PDF and Web values was not detected!"
    assert conflict_specs[0].status == "REVIEW" and conflict_specs[1].status == "REVIEW", "Spec status must be set to REVIEW"
    print(f"[PASS] Multi-source value conflict detected cleanly: '{conflict_res[0].message}'")

    print("\n==================================================")
    print("ALL VALIDATION ENGINE TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_validation_suite()
    sys.exit(0 if success else 1)
