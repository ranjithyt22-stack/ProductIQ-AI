"""
Automated Test Suite for Transparent Unit Normalization & Lineage Tracking (Phase 2).
Tests unit conversions (e.g., MPa to bar), standardizations, value-unit separation, and rule recording.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from backend.normalization import (
    normalize_unit, separate_value_and_unit, convert_unit_equivalences, normalize_specification
)


class TestNormalizationLineage(unittest.TestCase):

    def test_01_unit_conversion_mpa_to_bar(self):
        """Test standard industrial unit conversion from MPa to bar (1 MPa = 10 bar)."""
        val, unit, applied, rule = convert_unit_equivalences("1", "MPa")
        self.assertEqual(val, "10")
        self.assertEqual(unit, "bar")
        self.assertTrue(applied)
        self.assertIn("MPa_to_bar", rule)

        # Range conversion
        val_rng, unit_rng, app_rng, rule_rng = convert_unit_equivalences("0.1 to 1", "MPa")
        self.assertEqual(val_rng, "1 to 10")
        self.assertEqual(unit_rng, "bar")
        self.assertTrue(app_rng)

    def test_02_unit_standardization_and_separation(self):
        """Test value-unit separation and canonical unit standardization."""
        test_cases = [
            ("50 mm", None, "50", "mm"),
            ("1 to 10 bar", None, "1 to 10", "bar"),
            ("-20 to 80 deg c", None, "-20 to 80", "°C"),
            ("24V", None, "24", "V"),
            ("1.5 kilograms", None, "1.5", "kg"),
        ]

        for raw_in, unit_in, exp_val, exp_unit in test_cases:
            val, unit, applied, rule = separate_value_and_unit(raw_in, unit_in)
            self.assertEqual(val, exp_val, f"Failed for {raw_in}")
            self.assertEqual(unit, exp_unit, f"Failed for {raw_in}")
            self.assertTrue(applied, f"Failed applied flag for {raw_in}")

    def test_03_normalize_specification_preserves_lineage(self):
        """Test that normalize_specification preserves both raw_value and normalized_value with rule."""
        spec = {
            "name": "Bore Diameter",
            "value": "50 mm",
            "unit": None
        }
        res = normalize_specification(spec)

        self.assertEqual(res["raw_value"], "50 mm")
        self.assertEqual(res["normalized_value"], "50")
        self.assertEqual(res["value"], "50")
        self.assertEqual(res["unit"], "mm")
        self.assertTrue(res["normalization_applied"])
        self.assertIsNotNone(res["normalization_rule"])


if __name__ == "__main__":
    unittest.main()
