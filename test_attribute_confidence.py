"""
Automated Test Suite for Attribute-Level Confidence Engine (Phase 2).
Tests multi-factor scoring, source reliability weighting, and threshold tier categorization.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from backend.models import MatchStatus, SourceReliability
from backend.confidence import calculate_attribute_confidence, get_confidence_tier


class TestAttributeConfidence(unittest.TestCase):

    def test_01_high_confidence_official_datasheet(self):
        """Test high confidence score (>=90) for direct datasheet citation with valid unit."""
        score = calculate_attribute_confidence(
            val_str="10",
            unit_str="bar",
            page_num=1,
            evidence_snippet="Operating pressure: 10 bar.",
            evidence_score=0.95,
            match_status=MatchStatus.VERIFIED,
            source_reliability=SourceReliability.OFFICIAL_DATASHEET,
            has_validation_warning=False
        )

        self.assertGreaterEqual(score, 90)
        self.assertEqual(get_confidence_tier(score), "HIGH")

    def test_02_source_reliability_weighting(self):
        """Test that third-party or user-supplied sources receive lower scores than official datasheets."""
        score_official = calculate_attribute_confidence(
            val_str="24",
            unit_str="V",
            page_num=1,
            evidence_snippet="Voltage: 24 V",
            evidence_score=0.9,
            match_status=MatchStatus.VERIFIED,
            source_reliability=SourceReliability.OFFICIAL_DATASHEET
        )

        score_user_input = calculate_attribute_confidence(
            val_str="24",
            unit_str="V",
            page_num=1,
            evidence_snippet="Voltage: 24 V",
            evidence_score=0.9,
            match_status=MatchStatus.VERIFIED,
            source_reliability=SourceReliability.USER_INPUT
        )

        self.assertGreater(score_official, score_user_input)
        self.assertGreaterEqual(score_official, 90)
        self.assertLessEqual(score_user_input, 60)

    def test_03_validation_warning_penalty(self):
        """Test score penalty when an engineering validation warning is triggered."""
        score_clean = calculate_attribute_confidence(
            val_str="50",
            unit_str="mm",
            page_num=1,
            evidence_snippet="Bore: 50 mm",
            evidence_score=0.9,
            match_status=MatchStatus.VERIFIED,
            has_validation_warning=False
        )

        score_warning = calculate_attribute_confidence(
            val_str="50",
            unit_str="mm",
            page_num=1,
            evidence_snippet="Bore: 50 mm",
            evidence_score=0.9,
            match_status=MatchStatus.VERIFIED,
            has_validation_warning=True
        )

        self.assertGreater(score_clean - score_warning, 25)

    def test_04_unverified_hallucination_zero_confidence(self):
        """Test that unverified / missing evidence attributes yield zero confidence."""
        score = calculate_attribute_confidence(
            val_str="3 years",
            unit_str="years",
            page_num=None,
            evidence_snippet="",
            evidence_score=0.0,
            match_status=MatchStatus.NOT_FOUND
        )

        self.assertEqual(score, 0)
        self.assertEqual(get_confidence_tier(score), "UNVERIFIED")

    def test_05_human_verified_override_full_confidence(self):
        """Test that human verified override returns 100% confidence."""
        score = calculate_attribute_confidence(
            val_str="120",
            unit_str="mm",
            page_num=1,
            evidence_snippet="Bore 120 mm",
            review_status="human_verified"
        )

        self.assertEqual(score, 100)
        self.assertEqual(get_confidence_tier(score), "HIGH")


if __name__ == "__main__":
    unittest.main()
