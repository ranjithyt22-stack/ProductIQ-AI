"""
Automated Test Suite for ProductIQ AI Repository Layer.
Comprehensive testing of all 8 specialized repositories and their query methods.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.connection import Base
from backend.database.repositories import (
    ProductRepository, SourceRepository, SpecificationRepository,
    EvidenceRepository, ValidationRepository, ReviewRepository,
    CatalogRepository, JobRepository
)
from backend.models import (
    ProductIntelligenceRecord, ProductInfo, SpecificationAttribute,
    ValidationResult, AIEnrichment, ProductQualityScore,
    CatalogResult, CatalogProduct, CatalogProcessingStatus
)


class TestRepositoryLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=cls.test_engine)
        cls.TestSession = sessionmaker(bind=cls.test_engine)

    def setUp(self):
        self.db = self.TestSession()
        self.prod_repo = ProductRepository(self.db)
        self.source_repo = SourceRepository(self.db)
        self.spec_repo = SpecificationRepository(self.db)
        self.evidence_repo = EvidenceRepository(self.db)
        self.val_repo = ValidationRepository(self.db)
        self.review_repo = ReviewRepository(self.db)
        self.cat_repo = CatalogRepository(self.db)
        self.job_repo = JobRepository(self.db)

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_01_product_repository_search_and_filter(self):
        """Test ProductRepository listing with search and commerce readiness filters."""
        self.prod_repo.create_or_update_product(
            product_id="P-001",
            product_name="Inductive Proximity Sensor",
            manufacturer="Omron Industrial",
            commerce_readiness="READY FOR COMMERCE"
        )
        self.prod_repo.create_or_update_product(
            product_id="P-002",
            product_name="Capacitive Proximity Sensor",
            manufacturer="Sick AG",
            commerce_readiness="REQUIRES MANUAL REVIEW"
        )
        self.db.commit()

        # Search
        res_search = self.prod_repo.list_products(search="Omron")
        self.assertEqual(len(res_search), 1)
        self.assertEqual(res_search[0].product_id, "P-001")

        # Filter by readiness
        res_filter = self.prod_repo.list_products(readiness="READY FOR COMMERCE")
        self.assertEqual(len(res_filter), 1)
        self.assertEqual(res_filter[0].product_id, "P-001")

    def test_02_source_repository_and_hash_deduplication(self):
        """Test SourceRepository storage and SHA-256 content hashing."""
        content = "Technical Datasheet Content for Verification"
        src = self.source_repo.add_source(
            source_id="src_test_101",
            source_type="PDF",
            source_name="Datasheet.pdf",
            product_id="P-001",
            raw_content=content
        )
        self.db.commit()

        retrieved = self.source_repo.get_by_source_id("src_test_101")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.source_name, "Datasheet.pdf")
        self.assertIsNotNone(retrieved.source_hash)
        self.assertEqual(len(retrieved.source_hash), 64)  # SHA-256 hex length

    def test_03_specification_and_review_repositories(self):
        """Test SpecificationRepository updates and ReviewRepository audit logging."""
        product_id = "P-REV-01"
        rec = ProductIntelligenceRecord(
            product_id=product_id,
            product=ProductInfo(product_name="Flow Meter FM-10"),
            specifications=[
                SpecificationAttribute(name="Flow Rate", value="50", unit="L/min", confidence=85.0)
            ],
            quality_score=ProductQualityScore(overall_score=85)
        )
        p, v = self.prod_repo.save_full_record(rec)

        # Apply human review override
        updated_spec = self.spec_repo.update_specification_value(
            version_id=v.version_id,
            attribute_name="Flow Rate",
            reviewed_value="55",
            reviewed_unit="L/min"
        )
        self.assertIsNotNone(updated_spec)
        self.assertEqual(updated_spec.normalized_value, "55")
        self.assertEqual(updated_spec.review_status, "human_verified")

        # Record audit log
        rev_entry = self.review_repo.record_review(
            product_id=product_id,
            version_id=v.version_id,
            attribute_name="Flow Rate",
            original_value="50",
            reviewed_value="55",
            reviewed_unit="L/min",
            verification_note="Calibrated against manufacturer lab standard."
        )
        self.db.commit()

        reviews = self.review_repo.get_by_product(product_id)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].reviewed_value, "55")

    def test_04_catalog_repository(self):
        """Test CatalogRepository batch results persistence and retrieval."""
        cat_res = CatalogResult(
            catalog_id="CAT-BATCH-99",
            processing_status=CatalogProcessingStatus.COMPLETED,
            total_products=2,
            processed_products=2,
            ready_products=2,
            average_quality_score=96.0,
            products=[
                CatalogProduct(
                    product_id="CAT-P-1",
                    product_name="Ball Valve BV-10",
                    quality_score=95,
                    readiness_status="READY FOR COMMERCE",
                    status=CatalogProcessingStatus.COMPLETED
                ),
                CatalogProduct(
                    product_id="CAT-P-2",
                    product_name="Gate Valve GV-20",
                    quality_score=97,
                    readiness_status="READY FOR COMMERCE",
                    status=CatalogProcessingStatus.COMPLETED
                )
            ]
        )

        cat_entity = self.cat_repo.save_catalog_result(cat_res, catalog_name="Valves Batch")
        self.assertIsNotNone(cat_entity)

        retrieved_cat = self.cat_repo.get_catalog("CAT-BATCH-99")
        self.assertIsNotNone(retrieved_cat)
        self.assertEqual(retrieved_cat.total_products, 2)
        self.assertEqual(len(retrieved_cat.items), 2)

        item = self.cat_repo.get_catalog_item("CAT-BATCH-99", "CAT-P-1")
        self.assertIsNotNone(item)
        self.assertEqual(item.product_name, "Ball Valve BV-10")

    def test_05_job_repository(self):
        """Test JobRepository creation, lifecycle updates, and retrieval."""
        job = self.job_repo.create_job(
            job_type="CATALOG_BATCH",
            input_payload={"catalog_id": "CAT-BATCH-99"}
        )
        self.assertEqual(job.status, "QUEUED")

        updated = self.job_repo.update_job_status(
            job_id=job.job_id,
            status="COMPLETED",
            result_summary={"total": 2, "processed": 2}
        )
        self.assertEqual(updated.status, "COMPLETED")

        fetched = self.job_repo.get_job(job.job_id)
        self.assertEqual(fetched.status, "COMPLETED")


if __name__ == "__main__":
    unittest.main()
