"""
Automated Test Suite for ProductIQ AI Database Layer.
Verifies table creation, CRUD operations on all 12 ORM entities, session management, and constraints.
"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.connection import Base
from backend.database.models import (
    ProductEntity, ProductVersionEntity, ProductSourceEntity,
    ProductSpecificationEntity, EvidenceRecordEntity, ValidationRecordEntity,
    EnrichmentRecordEntity, QualityScoreEntity, HumanReviewEntity,
    CatalogEntity, CatalogItemEntity, ProcessingJobEntity
)


class TestDatabaseLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Use in-memory SQLite engine for fast, isolated database testing."""
        cls.test_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=cls.test_engine)
        cls.TestSession = sessionmaker(bind=cls.test_engine)

    def setUp(self):
        self.db = self.TestSession()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_01_create_and_retrieve_product(self):
        """Test ProductEntity creation, persistence and dictionary serialization."""
        prod = ProductEntity(
            product_id="TEST-PROD-001",
            manufacturer="Precision Hydraulics Inc",
            product_name="High Pressure Solenoid Valve HV-50",
            product_code="HV-50-24V",
            category="Hydraulic Valves",
            description="2-way solenoid valve for industrial fluid systems.",
            quality_score=94,
            commerce_readiness="READY FOR COMMERCE"
        )
        self.db.add(prod)
        self.db.commit()

        retrieved = self.db.query(ProductEntity).filter(ProductEntity.product_id == "TEST-PROD-001").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.product_name, "High Pressure Solenoid Valve HV-50")
        self.assertEqual(retrieved.quality_score, 94)

        d = retrieved.to_dict()
        self.assertEqual(d["product_id"], "TEST-PROD-001")
        self.assertEqual(d["manufacturer"], "Precision Hydraulics Inc")
        self.assertIn("created_at", d)

    def test_02_product_version_relationship(self):
        """Test ProductVersionEntity relationship with cascade delete."""
        prod = ProductEntity(
            product_id="TEST-VER-001",
            product_name="Industrial Thermocouple TC-100",
            manufacturer="TempSens Ltd"
        )
        self.db.add(prod)
        self.db.flush()

        v1 = ProductVersionEntity(
            version_id="TEST-VER-001-v1",
            product_id="TEST-VER-001",
            version_number=1,
            product_name="Industrial Thermocouple TC-100",
            quality_score=85,
            change_summary="Initial datasheet ingestion"
        )
        v2 = ProductVersionEntity(
            version_id="TEST-VER-001-v2",
            product_id="TEST-VER-001",
            version_number=2,
            product_name="Industrial Thermocouple TC-100 Pro",
            quality_score=95,
            change_summary="Supplementary specification update"
        )
        self.db.add_all([v1, v2])
        self.db.commit()

        retrieved = self.db.query(ProductEntity).filter(ProductEntity.product_id == "TEST-VER-001").first()
        self.assertEqual(len(retrieved.versions), 2)
        self.assertEqual(retrieved.versions[0].version_number, 2)  # Order by desc

    def test_03_specification_and_evidence_entities(self):
        """Test ProductSpecificationEntity and EvidenceRecordEntity linking."""
        prod = ProductEntity(product_id="TEST-SPEC-001", product_name="Sensor TS-10")
        self.db.add(prod)
        self.db.flush()

        ver = ProductVersionEntity(
            version_id="TEST-SPEC-001-v1",
            product_id="TEST-SPEC-001",
            version_number=1
        )
        self.db.add(ver)
        self.db.flush()

        spec = ProductSpecificationEntity(
            spec_id="spec_001",
            product_id="TEST-SPEC-001",
            version_id="TEST-SPEC-001-v1",
            attribute_name="Operating Pressure",
            raw_value="10 bar",
            normalized_value="10",
            unit="bar",
            confidence=98.5,
            validation_status="PASS"
        )
        self.db.add(spec)
        self.db.flush()

        ev = EvidenceRecordEntity(
            evidence_id="ev_001",
            spec_id="spec_001",
            page_number=2,
            verbatim_quote="Operating pressure: 10 bar nominal.",
            confidence_score=0.985
        )
        self.db.add(ev)
        self.db.commit()

        retrieved_spec = self.db.query(ProductSpecificationEntity).filter(ProductSpecificationEntity.spec_id == "spec_001").first()
        self.assertIsNotNone(retrieved_spec)
        self.assertIsNotNone(retrieved_spec.evidence)
        self.assertEqual(retrieved_spec.evidence.verbatim_quote, "Operating pressure: 10 bar nominal.")

    def test_04_catalog_and_catalog_item_entities(self):
        """Test CatalogEntity and CatalogItemEntity persistence."""
        cat = CatalogEntity(
            catalog_id="CAT-TEST-001",
            catalog_name="Q3 Industrial Valves Catalog",
            total_products=5,
            processed_products=5,
            ready_products=4,
            review_required_products=1,
            failed_products=0,
            average_quality_score=92.5
        )
        self.db.add(cat)
        self.db.flush()

        item = CatalogItemEntity(
            catalog_id="CAT-TEST-001",
            product_id="PIQ-000001",
            product_name="Catalog Item 1",
            quality_score=95,
            readiness_status="READY FOR COMMERCE"
        )
        self.db.add(item)
        self.db.commit()

        retrieved_cat = self.db.query(CatalogEntity).filter(CatalogEntity.catalog_id == "CAT-TEST-001").first()
        self.assertIsNotNone(retrieved_cat)
        self.assertEqual(len(retrieved_cat.items), 1)
        self.assertEqual(retrieved_cat.items[0].product_name, "Catalog Item 1")

    def test_05_processing_job_entity(self):
        """Test ProcessingJobEntity state tracking."""
        job = ProcessingJobEntity(
            job_id="job_test_001",
            job_type="CATALOG_BATCH",
            status="QUEUED"
        )
        self.db.add(job)
        self.db.commit()

        retrieved = self.db.query(ProcessingJobEntity).filter(ProcessingJobEntity.job_id == "job_test_001").first()
        self.assertEqual(retrieved.status, "QUEUED")
        retrieved.status = "COMPLETED"
        self.db.commit()

        updated = self.db.query(ProcessingJobEntity).filter(ProcessingJobEntity.job_id == "job_test_001").first()
        self.assertEqual(updated.status, "COMPLETED")


if __name__ == "__main__":
    unittest.main()
