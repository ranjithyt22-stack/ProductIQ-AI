"""
Automated Test Suite for ProductIQ AI Explainability & Diagnostic Records (Phase 2).
Tests structured explainability records, diagnostic review reasons, and factual transparency.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from backend.models import SpecificationAttribute, ValidationResult, MatchStatus, EvidenceType
from backend.explainability import generate_attribute_explainability, build_product_explainability


class TestExplainability(unittest.TestCase):

    def test_01_verified_attribute_explainability(self):
        """Test clean explainability record for verified attribute."""
        spec = SpecificationAttribute(
            name="Operating Pressure",
            value="1 to 10",
            unit="bar",
            raw_value="1 to 10 bar",
            normalized_value="1 to 10",
            normalization_applied=True,
            normalization_rule="extract_range_unit (bar -> bar)",
            page=1,
            evidence="Operating pressure range: 1 to 10 bar",
            evidence_id="ev_001",
            match_status=MatchStatus.VERIFIED,
            confidence=97.0,
            confidence_level="HIGH",
            status="PASS",
            review_status="ai_extracted"
        )

        validations = [
            ValidationResult(rule="Pressure Range", status="PASS", severity="INFO", message="Valid range", field="Operating Pressure")
        ]

        rec = generate_attribute_explainability(spec, validations)

        self.assertEqual(rec.attribute_name, "Operating Pressure")
        self.assertEqual(rec.final_value, "1 to 10 bar")
        self.assertEqual(rec.raw_value, "1 to 10 bar")
        self.assertEqual(rec.normalized_value, "1 to 10")
        self.assertEqual(rec.evidence_status, MatchStatus.VERIFIED)
        self.assertEqual(rec.normalization_status, "SUCCESS")
        self.assertEqual(rec.validation_status, "PASS")
        self.assertEqual(rec.confidence, 97)
        self.assertEqual(rec.confidence_level, "HIGH")
        self.assertFalse(rec.review_required)
        self.assertEqual(rec.final_status, "VERIFIED")

    def test_02_unverified_attribute_explainability_reason(self):
        """Test diagnostic review reason for unverified hallucinated attribute."""
        spec = SpecificationAttribute(
            name="Warranty Period",
            value="2",
            unit="years",
            raw_value="2 years",
            normalized_value="2",
            page=None,
            evidence="",
            match_status=MatchStatus.NOT_FOUND,
            evidence_type=EvidenceType.UNVERIFIED,
            confidence=0.0,
            confidence_level="UNVERIFIED",
            status="UNVERIFIED",
            review_status="ai_extracted"
        )

        rec = generate_attribute_explainability(spec, [])

        self.assertTrue(rec.review_required)
        self.assertIn("Evidence was not found", rec.review_reason)
        self.assertEqual(rec.final_status, "UNVERIFIED")

    def test_03_conflicting_attribute_explainability_reason(self):
        """Test diagnostic reason for cross-source conflict."""
        spec = SpecificationAttribute(
            name="Supply Voltage",
            value="24",
            unit="V",
            raw_value="24 V",
            normalized_value="24",
            page=1,
            evidence="24 V DC",
            match_status=MatchStatus.CONFLICTING,
            confidence=60.0,
            confidence_level="LOW",
            status="REVIEW"
        )

        rec = generate_attribute_explainability(spec, [], cross_source_conflicts=["Supply Voltage"])

        self.assertTrue(rec.review_required)
        self.assertEqual(rec.cross_source_status, "CONFLICT")
        self.assertIn("Multiple sources contain conflicting values", rec.review_reason)


if __name__ == "__main__":
    unittest.main()
