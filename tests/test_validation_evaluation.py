"""
Test Suite for Validation Engine Benchmark Accuracy & Rule Enforcement.
"""

import pytest
from backend.validation import validate_product_data
from backend.models import ProductInfo, SpecificationAttribute


def test_validation_detects_negative_operating_pressure():
    p_info = ProductInfo(
        product_name="Pressure Pump",
        manufacturer="Apex",
        product_code="AP-100",
        category="Hydraulic Pump"
    )

    specs = [
        SpecificationAttribute(
            name="Operating Pressure",
            value="-15",
            unit="bar",
            raw_value="-15 bar"
        )
    ]

    validations = validate_product_data(p_info, specs)
    warnings = [v for v in validations if v.status in ["WARNING", "FAIL", "REVIEW"]]

    # Should detect negative pressure
    assert len(warnings) > 0
    assert any("negative" in w.message.lower() or "pressure" in w.field.lower() for w in warnings)
