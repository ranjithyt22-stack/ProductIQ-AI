"""
Test Suite: Conflict Normalization & Equivalence Checking
Verifies that physically and semantically equivalent values across units (1 MPa == 10 bar,
1000 mm == 1 m, 1000 g == 1 kg, 1 kW == 1000 W, -20 to 80 C == -20-80 C)
do not trigger false-positive conflicts.
"""

import pytest
from backend.conflicts import are_values_equivalent, detect_product_conflicts
from backend.models import SpecificationAttribute, SourceReliability


def test_pressure_unit_equivalence_1mpa_10bar():
    """1 MPa and 10 bar are physically equivalent and must not trigger a conflict."""
    is_equiv, reason = are_values_equivalent("1", "MPa", "10", "bar")
    assert is_equiv is True
    assert "equivalence" in reason.lower()

    # Integration test with detect_product_conflicts
    specs = [
        SpecificationAttribute(
            name="Max Operating Pressure",
            value="1",
            unit="MPa",
            source_name="Source A (Datasheet)",
            source_reliability=SourceReliability.OFFICIAL_DATASHEET
        ),
        SpecificationAttribute(
            name="Max Operating Pressure",
            value="10",
            unit="bar",
            source_name="Source B (Website)",
            source_reliability=SourceReliability.OFFICIAL_WEBSITE
        )
    ]
    conflicts = detect_product_conflicts(product_id="PIQ-VALVE-01", specifications=specs)
    assert len(conflicts) == 0


def test_length_unit_equivalence_1000mm_1m():
    """1000 mm, 1 m, and 100 cm must be equivalent."""
    is_equiv, _ = are_values_equivalent("1000", "mm", "1", "m")
    assert is_equiv is True

    is_equiv_cm, _ = are_values_equivalent("100", "cm", "1000", "mm")
    assert is_equiv_cm is True


def test_mass_unit_equivalence_1000g_1kg():
    """1000 g and 1 kg must be equivalent."""
    is_equiv, _ = are_values_equivalent("1000", "g", "1", "kg")
    assert is_equiv is True


def test_power_unit_equivalence_1kw_1000w():
    """1 kW and 1000 W must be equivalent."""
    is_equiv, _ = are_values_equivalent("1", "kW", "1000", "W")
    assert is_equiv is True


def test_casing_and_spacing_equivalence():
    """10 BAR, 10 bar, 10Bar must be equivalent."""
    is_equiv_1, _ = are_values_equivalent("10", "BAR", "10", "bar")
    assert is_equiv_1 is True

    is_equiv_2, _ = are_values_equivalent("10", "bar", "10", "Bar")
    assert is_equiv_2 is True


def test_range_format_equivalence():
    """-20 to 80 °C and -20 - 80 °C must be equivalent."""
    is_equiv, _ = are_values_equivalent("-20 to 80", "deg C", "-20-80", "deg C")
    assert is_equiv is True


def test_actual_difference_detected_as_not_equivalent():
    """10 bar and 16 bar must be flagged as non-equivalent."""
    is_equiv, _ = are_values_equivalent("10", "bar", "16", "bar")
    assert is_equiv is False
