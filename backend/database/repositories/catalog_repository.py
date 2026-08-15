"""
Catalog repository for ProductIQ AI.
Handles persistence and querying of batch catalog runs and individual catalog item records.
"""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database.models import CatalogEntity, CatalogItemEntity
from backend.models import CatalogResult


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_catalog_result(self, cat_result: CatalogResult, catalog_name: Optional[str] = None) -> CatalogEntity:
        """Persists a full CatalogResult and its associated catalog items."""
        cat_entity = (
            self.db.query(CatalogEntity)
            .filter(CatalogEntity.catalog_id == cat_result.catalog_id)
            .first()
        )

        if not cat_entity:
            cat_entity = CatalogEntity(
                catalog_id=cat_result.catalog_id,
                catalog_name=catalog_name or f"Catalog {cat_result.catalog_id}",
                processing_status=cat_result.processing_status,
                total_products=cat_result.total_products,
                processed_products=cat_result.processed_products,
                ready_products=cat_result.ready_products,
                review_required_products=cat_result.review_required_products,
                failed_products=cat_result.failed_products,
                average_quality_score=cat_result.average_quality_score,
                average_evidence_coverage=cat_result.average_evidence_coverage,
                validation_pass_rate=cat_result.validation_pass_rate
            )
            self.db.add(cat_entity)
        else:
            cat_entity.processing_status = cat_result.processing_status
            cat_entity.total_products = cat_result.total_products
            cat_entity.processed_products = cat_result.processed_products
            cat_entity.ready_products = cat_result.ready_products
            cat_entity.review_required_products = cat_result.review_required_products
            cat_entity.failed_products = cat_result.failed_products
            cat_entity.average_quality_score = cat_result.average_quality_score
            cat_entity.average_evidence_coverage = cat_result.average_evidence_coverage
            cat_entity.validation_pass_rate = cat_result.validation_pass_rate

        self.db.flush()

        # Save individual items
        for p in cat_result.products:
            item_entity = (
                self.db.query(CatalogItemEntity)
                .filter(
                    CatalogItemEntity.catalog_id == cat_result.catalog_id,
                    CatalogItemEntity.product_id == p.product_id
                )
                .first()
            )

            rec_json = json.dumps(p.record.to_dict()) if p.record else None

            if not item_entity:
                item_entity = CatalogItemEntity(
                    catalog_id=cat_result.catalog_id,
                    product_id=p.product_id,
                    product_name=p.product_name,
                    manufacturer=p.manufacturer,
                    product_code=p.product_code,
                    category=p.category,
                    quality_score=p.quality_score,
                    readiness_status=p.readiness_status,
                    processing_status=p.status,
                    error_message=p.error_message,
                    record_json=rec_json
                )
                self.db.add(item_entity)
            else:
                item_entity.product_name = p.product_name
                item_entity.manufacturer = p.manufacturer
                item_entity.product_code = p.product_code
                item_entity.category = p.category
                item_entity.quality_score = p.quality_score
                item_entity.readiness_status = p.readiness_status
                item_entity.processing_status = p.status
                item_entity.error_message = p.error_message
                item_entity.record_json = rec_json

        self.db.commit()
        return cat_entity

    def get_catalog(self, catalog_id: str) -> Optional[CatalogEntity]:
        """Retrieves a catalog by catalog_id."""
        return self.db.query(CatalogEntity).filter(CatalogEntity.catalog_id == catalog_id).first()

    def list_catalogs(self, limit: int = 50) -> List[CatalogEntity]:
        """Lists recent catalogs."""
        return self.db.query(CatalogEntity).order_by(desc(CatalogEntity.created_at)).limit(limit).all()

    def get_catalog_item(self, catalog_id: str, product_id: str) -> Optional[CatalogItemEntity]:
        """Retrieves a specific catalog item."""
        return (
            self.db.query(CatalogItemEntity)
            .filter(
                CatalogItemEntity.catalog_id == catalog_id,
                CatalogItemEntity.product_id == product_id
            )
            .first()
        )
