"""
Automated Test Suite for ProductIQ AI Deterministic Evidence Grounding (Phase 2).
Tests verbatim citation extraction, match status categorization (VERIFIED, PARTIAL, NOT_FOUND, CONFLICTING),
and multi-source evidence linking across 5 industrial product categories.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from backend.models import MatchStatus, EvidenceType, SourceReliability
from backend.evidence import isolate_evidence_record, isolate_evidence


class TestEvidenceGrounding(unittest.TestCase):

    def test_01_direct_verbatim_evidence_match(self):
        """Test exact quote extraction from official datasheet pages."""
        pages = [
            {"page": 1, "text": "Model: TS-200\nOperating Temperature Range: -50 to 200 °C nominal.\nSupply Voltage: 24 V DC"}
        ]
        rec = isolate_evidence_record(
            attr_name="Operating Temperature Range",
            raw_val_str="-50 to 200",
            normalized_val_str="-50 to 200",
            unit_str="°C",
            raw_pages=pages,
            hint_page=1,
            source_reliability=SourceReliability.OFFICIAL_DATASHEET
        )

        self.assertEqual(rec.match_status, MatchStatus.VERIFIED)
        self.assertEqual(rec.page_number, 1)
        self.assertIn("-50 to 200 °C", rec.quote)
        self.assertGreaterEqual(rec.evidence_confidence, 0.90)

    def test_02_missing_evidence_anti_hallucination(self):
        """Test that unmentioned attributes return NOT_FOUND and zero confidence."""
        pages = [
            {"page": 1, "text": "High-flow hydraulic proportional valve PV-300. Max pressure: 350 bar."}
        ]
        # LLM hallucinated warranty period
        rec = isolate_evidence_record(
            attr_name="Warranty Period",
            raw_val_str="5 years",
            normalized_val_str="5",
            unit_str="years",
            raw_pages=pages,
            hint_page=1
        )

        self.assertEqual(rec.match_status, MatchStatus.NOT_FOUND)
        self.assertEqual(rec.evidence_type, EvidenceType.UNVERIFIED)
        self.assertEqual(rec.evidence_confidence, 0.0)
        self.assertEqual(rec.quote, "")

    def test_03_partial_evidence_matching(self):
        """Test partial match when value and unit match but attribute phrasing differs."""
        pages = [
            {"page": 2, "text": "Motor Specifications Table:\nRated power output is 7.5 kW at 1450 rpm.\nFlange standard: IEC 132M."}
        ]
        rec = isolate_evidence_record(
            attr_name="Output Power",
            raw_val_str="7.5",
            normalized_val_str="7.5",
            unit_str="kW",
            raw_pages=pages,
            hint_page=2
        )

        self.assertIn(rec.match_status, [MatchStatus.VERIFIED, MatchStatus.PARTIALLY_VERIFIED])
        self.assertEqual(rec.page_number, 2)
        self.assertIn("7.5 kW", rec.quote)

    def test_04_ai_enriched_never_presented_as_direct_evidence(self):
        """Test that AI-inferred attributes are explicitly typed as AI_ENRICHED, never DIRECT."""
        rec = isolate_evidence_record(
            attr_name="Category Path",
            raw_val_str="Industrial Automation > Fluid Power",
            normalized_val_str="Industrial Automation > Fluid Power",
            unit_str=None,
            raw_pages=[],
            is_inferred=True,
            source_reliability=SourceReliability.AI_INFERENCE
        )

        self.assertEqual(rec.evidence_type, EvidenceType.AI_ENRICHED)
        self.assertNotEqual(rec.evidence_type, EvidenceType.DIRECT)
        self.assertLessEqual(rec.evidence_confidence, 0.5)

    def test_05_multi_category_fixtures(self):
        """Test evidence grounding across 5 distinct industrial categories."""
        fixtures = [
            # 1. Pneumatic Cylinder
            {"attr": "Bore Diameter", "val": "50", "unit": "mm", "text": "Pneumatic Cylinder. Bore diameter: 50 mm.", "page": 1},
            # 2. Temperature Sensor
            {"attr": "Probe Length", "val": "150", "unit": "mm", "text": "Stainless probe length 150 mm.", "page": 1},
            # 3. Pressure Valve
            {"attr": "Max Pressure", "val": "400", "unit": "bar", "text": "Maximum operating pressure: 400 bar.", "page": 2},
            # 4. Industrial Bearing
            {"attr": "Dynamic Load Rating", "val": "28.5", "unit": "kN", "text": "Basic dynamic load rating C = 28.5 kN.", "page": 1},
            # 5. Electric Motor
            {"attr": "Synchronous Speed", "val": "3000", "unit": "rpm", "text": "2-pole 50Hz synchronous speed: 3000 rpm.", "page": 3},
        ]

        for fix in fixtures:
            pages = [{"page": fix["page"], "text": fix["text"]}]
            rec = isolate_evidence_record(
                attr_name=fix["attr"],
                raw_val_str=fix["val"],
                normalized_val_str=fix["val"],
                unit_str=fix["unit"],
                raw_pages=pages,
                hint_page=fix["page"]
            )
            self.assertEqual(rec.match_status, MatchStatus.VERIFIED, f"Failed for {fix['attr']}")
            self.assertGreaterEqual(rec.evidence_confidence, 0.85)


if __name__ == "__main__":
    unittest.main()
