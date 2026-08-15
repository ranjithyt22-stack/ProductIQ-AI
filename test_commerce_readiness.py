"""
Automated Test Suite for Deterministic Commerce Readiness Engine (Phase 2).
Tests commerce gating logic: NOT_READY, REVIEW_REQUIRED, READY_FOR_COMMERCE, HUMAN_VERIFIED.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from backend.models import (
    ProductInfo, SpecificationAttribute, ValidationResult,
    CommerceReadinessStatus, MatchStatus
)
from backend.scoring import calculate_quality_score


class TestCommerceReadiness(unittest.TestCase):

    def test_01_ready_for_commerce_clean_product(self):
        """Test that a complete, verified product with passing validations achieves READY_FOR_COMMERCE."""
        prod = ProductInfo(
            product_name="Electric Motor EM-100",
            manufacturer="Siemens Industrial",
            product_code="EM-100-4P",
            category="Electric Motors",
            description="3-phase industrial induction motor."
        )

        specs = [
            SpecificationAttribute(name="Rated Power", value="15", unit="kW", confidence=98.0, match_status=MatchStatus.VERIFIED, evidence="15 kW", status="PASS"),
            SpecificationAttribute(name="Rated Speed", value="1450", unit="rpm", confidence=96.0, match_status=MatchStatus.VERIFIED, evidence="1450 rpm", status="PASS"),
            SpecificationAttribute(name="Supply Voltage", value="400", unit="V", confidence=99.0, match_status=MatchStatus.VERIFIED, evidence="400 V", status="PASS"),
        ]

        validations = [
            ValidationResult(rule="Voltage Standard", status="PASS", severity="INFO", message="Valid", field="Supply Voltage")
        ]

        qs = calculate_quality_score(prod, specs, validations)
        self.assertEqual(qs.status_category, CommerceReadinessStatus.READY_FOR_COMMERCE)
        self.assertGreaterEqual(qs.overall_score, 85)

    def test_02_review_required_on_unresolved_conflict(self):
        """Test that a product with conflicting specifications is gated with REVIEW_REQUIRED."""
        prod = ProductInfo(
            product_name="Electric Motor EM-100",
            manufacturer="Siemens Industrial",
            product_code="EM-100-4P",
            category="Electric Motors",
            description="3-phase motor."
        )

        specs = [
            SpecificationAttribute(name="Supply Voltage", value="400", unit="V", confidence=50.0, match_status=MatchStatus.CONFLICTING, status="REVIEW", review_required=True),
        ]

        validations = [
            ValidationResult(rule="Multi-Source Conflict Check", status="WARNING", severity="HIGH", message="Conflict on Voltage", field="Supply Voltage")
        ]

        qs = calculate_quality_score(prod, specs, validations)
        self.assertEqual(qs.status_category, CommerceReadinessStatus.REVIEW_REQUIRED)

    def test_03_human_verified_readiness(self):
        """Test that human-in-the-loop review override promotes status to HUMAN_VERIFIED."""
        prod = ProductInfo(
            product_name="Electric Motor EM-100",
            manufacturer="Siemens Industrial",
            product_code="EM-100-4P",
            category="Electric Motors",
            description="3-phase motor."
        )

        specs = [
            SpecificationAttribute(name="Supply Voltage", value="400", unit="V", confidence=100.0, match_status=MatchStatus.VERIFIED, review_status="human_verified", status="PASS"),
        ]

        validations = [
            ValidationResult(rule="Voltage Standard", status="PASS", severity="INFO", message="Valid", field="Supply Voltage")
        ]

        qs = calculate_quality_score(prod, specs, validations)
        self.assertEqual(qs.status_category, CommerceReadinessStatus.HUMAN_VERIFIED)

    def test_04_not_ready_on_missing_identity(self):
        """Test that a product missing core name or specifications returns NOT_READY."""
        prod = ProductInfo(product_name=None)
        qs = calculate_quality_score(prod, [], [])
        self.assertEqual(qs.status_category, CommerceReadinessStatus.NOT_READY)


if __name__ == "__main__":
    unittest.main()
