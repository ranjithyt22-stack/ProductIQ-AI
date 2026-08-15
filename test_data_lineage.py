"""
Automated Test Suite for ProductIQ AI Data Lineage Tracing.
Verifies complete trace graph: Product -> Version -> Specification -> Source -> Evidence -> Normalization -> Validation -> Review.
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


class TestDataLineage(unittest.TestCase):

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

    def test_01_full_data_lineage_graph(self):
        """Test complete lineage reconstruction for an analyzed product."""
        product_id = "LINEAGE-TEST-100"

        rec = ProductIntelligenceRecord(
            product_id=product_id,
            product=ProductInfo(
                product_name="Proportional Pressure Regulator PR-20",
                manufacturer="Fluitec Fluidics Corp",
                product_code="PR-20-10B",
                category="Regulators",
                description="Electro-pneumatic pressure regulator."
            ),
            specifications=[
                SpecificationAttribute(
                    name="Max Operating Pressure",
                    value="16",
                    unit="bar",
                    original_value="16 bar",
                    page=3,
                    evidence="Maximum inlet operating pressure: 16 bar.",
                    confidence=99.0,
                    source_id="src_pdf_01",
                    source_name="Datasheet_PR20.pdf",
                    status="PASS",
                    review_status="ai_extracted"
                ),
                SpecificationAttribute(
                    name="Supply Voltage",
                    value="24",
                    unit="V DC",
                    original_value="24 V DC",
                    page=1,
                    evidence="Nominal control supply voltage: 24 V DC +-10%.",
                    confidence=97.0,
                    source_id="src_pdf_01",
                    source_name="Datasheet_PR20.pdf",
                    status="PASS",
                    review_status="human_verified"
                )
            ],
            validation=[
                ValidationResult(rule="Pressure Range Sanity", status="PASS", severity="INFO", message="Valid range", field="Max Operating Pressure"),
                ValidationResult(rule="Voltage Standard", status="PASS", severity="INFO", message="Valid voltage", field="Supply Voltage")
            ],
            enrichment=AIEnrichment(
                search_terms=["proportional regulator", "pressure control valve", "PR-20"],
                category_path=["Fluid Power", "Pneumatics", "Pressure Regulators"]
            ),
            quality_score=ProductQualityScore(
                overall_score=97,
                completeness=100,
                evidence_coverage=100,
                status_category="READY FOR COMMERCE"
            ),
            raw_sources=[
                {
                    "source_id": "src_pdf_01",
                    "source_type": "PDF",
                    "filename": "Datasheet_PR20.pdf",
                    "source_uri": "uploads/Datasheet_PR20.pdf"
                }
            ]
        )

        self.repo.save_full_record(rec, change_summary="Ingested PR-20 Datasheet")

        # Query lineage
        lineage = self.repo.get_lineage(product_id)

        self.assertNotIn("error", lineage)
        self.assertEqual(lineage["product"]["product_id"], product_id)
        self.assertEqual(lineage["version"]["version_number"], 1)

        # Check lineage items
        items = lineage["lineage_items"]
        self.assertEqual(len(items), 2)

        # Item 1: Max Operating Pressure
        p_item = items[0]
        self.assertEqual(p_item["specification"]["attribute_name"], "Max Operating Pressure")
        self.assertEqual(p_item["specification"]["normalized_value"], "16")
        self.assertEqual(p_item["specification"]["unit"], "bar")
        self.assertEqual(p_item["source"]["source_name"], "Datasheet_PR20.pdf")
        self.assertEqual(p_item["source"]["page_number"], 3)
        self.assertEqual(p_item["evidence"]["verbatim_quote"], "Maximum inlet operating pressure: 16 bar.")
        self.assertEqual(p_item["validation"]["status"], "PASS")

        # Summary checks
        summary = lineage["lineage_summary"]
        self.assertEqual(summary["total_attributes"], 2)
        self.assertEqual(summary["backed_by_verbatim_evidence"], 2)
        self.assertEqual(summary["validation_passed"], 2)
        self.assertEqual(summary["human_verified"], 1)


if __name__ == "__main__":
    unittest.main()
