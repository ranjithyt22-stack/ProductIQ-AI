"""
Unit and Integration Tests for Deterministic Multi-Attribute Global Search.
"""

import pytest
from backend.database.connection import get_db_context
from backend.database.models import ProductEntity
from backend.search import search_products


def test_search_products_filter_and_matching():
    with get_db_context() as db:
        # Create test product if not existing
        existing = db.query(ProductEntity).filter(ProductEntity.product_id == "prod_search_test_01").first()
        if not existing:
            p = ProductEntity(
                product_id="prod_search_test_01",
                product_name="High-Pressure Pneumatic Cylinder Apex",
                product_code="HPC-100-APEX",
                manufacturer="Apex Dynamics Inc.",
                category="Pneumatic Cylinder",
                commerce_readiness="READY_FOR_COMMERCE",
                quality_score=98.0
            )
            db.add(p)
            db.commit()

        # 1. Search by exact keyword
        res = search_products(db, query="Apex")
        assert res["total_count"] >= 1
        found_apex = any(x["product_id"] == "prod_search_test_01" for x in res["products"])
        assert found_apex is True

        # 2. Search by category filter
        res_cat = search_products(db, category="Pneumatic Cylinder")
        assert res_cat["total_count"] >= 1

        # 3. Search by commerce readiness
        res_ready = search_products(db, commerce_status="READY_FOR_COMMERCE")
        assert res_ready["total_count"] >= 1
