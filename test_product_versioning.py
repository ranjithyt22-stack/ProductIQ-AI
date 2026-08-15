"""
Automated Test Suite for ProductIQ AI Product Versioning & Comparison.
Verifies immutable snapshot retention, version incrementation, and specification diff generation.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.connection import Base
from backend.database.repositories.product_repository import ProductRepository
from backend.models import (
    ProductIntelligenceRecord, ProductInfo, SpecificationAttribute,
    ValidationResult, AIEnrichment, ProductQualityScore
)


class TestProductVersioning(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=cls.test_engine)
        cls.TestSession = sessionmaker(bind=cls.test_engine)

    def setUp(self):
        self.db = self.TestSession()
        self.repo = ProductRepository(self.db)

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_01_version_creation_and_preservation(self):
        """Verify that updating a product creates a new version while preserving the previous snapshot."""
        product_id = "PROD-VER-TEST-001"

        # 1. Create Version 1 (Initial Analysis: Temperature Range = -10 to 60 degC)
        rec_v1 = ProductIntelligenceRecord(
            product_id=product_id,
            product=ProductInfo(
                product_name="Digital Temperature Transmitter TT-400",
                manufacturer="Apex Sensors Corp",
                product_code="TT-400-A",
                category="Transmitters",
                description="Initial model release specification."
            ),
            specifications=[
                SpecificationAttribute(name="Operating Temperature", value="-10 to 60", unit="degC", confidence=95.0, status="PASS"),
                SpecificationAttribute(name="Supply Voltage", value="24", unit="V", confidence=98.0, status="PASS"),
            ],
            validation=[
                ValidationResult(rule="Unit Standard", status="PASS", severity="INFO", message="Valid unit", field="Operating Temperature")
            ],
            quality_score=ProductQualityScore(overall_score=88, status_category="REVIEW RECOMMENDED")
        )

        p1, ver1 = self.repo.save_full_record(rec_v1, change_summary="V1 initial datasheet")
        self.assertEqual(ver1.version_number, 1)
        self.assertEqual(ver1.version_id, f"{product_id}-v1")

        # 2. Create Version 2 (Revised Analysis: Temperature Range updated to -20 to 80 degC, new Accuracy spec added)
        rec_v2 = ProductIntelligenceRecord(
            product_id=product_id,
            product=ProductInfo(
                product_name="Digital Temperature Transmitter TT-400 Pro",
                manufacturer="Apex Sensors Corp",
                product_code="TT-400-A",
                category="Transmitters",
                description="Revised high-temperature revision specification."
            ),
            specifications=[
                SpecificationAttribute(name="Operating Temperature", value="-20 to 80", unit="degC", confidence=99.0, status="PASS"),
                SpecificationAttribute(name="Supply Voltage", value="24", unit="V", confidence=98.0, status="PASS"),
                SpecificationAttribute(name="Accuracy", value="0.1", unit="%", confidence=96.0, status="PASS"),
            ],
            validation=[
                ValidationResult(rule="Unit Standard", status="PASS", severity="INFO", message="Valid unit", field="Operating Temperature")
            ],
            quality_score=ProductQualityScore(overall_score=96, status_category="READY FOR COMMERCE")
        )

        p2, ver2 = self.repo.save_full_record(rec_v2, change_summary="V2 revised datasheet with wider temperature range")
        self.assertEqual(ver2.version_number, 2)
        self.assertEqual(ver2.version_id, f"{product_id}-v2")

        # 3. Verify Both Versions Are Preserved Independently
        versions = self.repo.get_versions(product_id)
        self.assertEqual(len(versions), 2)

        v1_check = self.repo.get_version(product_id, 1)
        v2_check = self.repo.get_version(product_id, 2)

        self.assertIsNotNone(v1_check)
        self.assertIsNotNone(v2_check)

        v1_temp_spec = [s for s in v1_check.specifications if s.attribute_name == "Operating Temperature"][0]
        v2_temp_spec = [s for s in v2_check.specifications if s.attribute_name == "Operating Temperature"][0]

        self.assertEqual(v1_temp_spec.normalized_value, "-10 to 60")
        self.assertEqual(v2_temp_spec.normalized_value, "-20 to 80")
        self.assertEqual(len(v1_check.specifications), 2)
        self.assertEqual(len(v2_check.specifications), 3)

    def test_02_version_comparison_diff(self):
        """Verify detailed diff generation between Version 1 and Version 2."""
        product_id = "PROD-VER-TEST-001"
        diff = self.repo.compare_versions(product_id, 1, 2)

        self.assertEqual(diff["product_id"], product_id)
        self.assertEqual(diff["v1"]["version_number"], 1)
        self.assertEqual(diff["v2"]["version_number"], 2)

        # Check metadata diff
        self.assertEqual(diff["metadata_diff"]["product_name"]["v1"], "Digital Temperature Transmitter TT-400")
        self.assertEqual(diff["metadata_diff"]["product_name"]["v2"], "Digital Temperature Transmitter TT-400 Pro")

        # Check specification diffs
        spec_diffs = {d["attribute"]: d for d in diff["specification_diffs"]}
        self.assertIn("Operating Temperature", spec_diffs)
        self.assertEqual(spec_diffs["Operating Temperature"]["change_type"], "MODIFIED")
        self.assertEqual(spec_diffs["Operating Temperature"]["v1_value"], "-10 to 60 degC")
        self.assertEqual(spec_diffs["Operating Temperature"]["v2_value"], "-20 to 80 degC")

        self.assertIn("Accuracy", spec_diffs)
        self.assertEqual(spec_diffs["Accuracy"]["change_type"], "ADDED")

        self.assertIn("Supply Voltage", spec_diffs)
        self.assertEqual(spec_diffs["Supply Voltage"]["change_type"], "UNCHANGED")


if __name__ == "__main__":
    unittest.main()
