"""
Test Suite for Cross-Source Conflict Benchmark Precision, Recall, and Equivalence.
"""

import pytest
from backend.conflicts import are_values_equivalent, detect_product_conflicts
from backend.models import SpecificationAttribute, ConflictType


def test_conflict_benchmark_cases():
    # 1. Real value mismatch: 10 bar vs 8 bar -> Conflict
    is_eq, reason = are_values_equivalent("10", "bar", "8", "bar")
    assert is_eq is False

    # 2. Pressure Equivalence: 1 MPa == 10 bar -> No Conflict
    is_eq, reason = are_values_equivalent("1", "MPa", "10", "bar")
    assert is_eq is True

    # 3. Dimension Equivalence: 1000 mm == 1 m -> No Conflict
    is_eq, reason = are_values_equivalent("1000", "mm", "1", "m")
    assert is_eq is True

    # 4. Mass Equivalence: 1000 g == 1 kg -> No Conflict
    is_eq, reason = are_values_equivalent("1000", "g", "1", "kg")
    assert is_eq is True

    # 5. Length mismatch: 50 mm vs 60 mm -> Conflict
    is_eq, reason = are_values_equivalent("50", "mm", "60", "mm")
    assert is_eq is False
