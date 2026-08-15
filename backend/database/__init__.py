"""
ProductIQ AI Persistence & Database Layer.
Provides SQLite/PostgreSQL-compatible ORM models, repositories, lineage tracing,
and versioning infrastructure.
"""

from backend.database.connection import get_db, init_db, engine, SessionLocal, Base
from backend.database.models import (
    ProductEntity, ProductVersionEntity, ProductSourceEntity,
    ProductSpecificationEntity, EvidenceRecordEntity, ValidationRecordEntity,
    EnrichmentRecordEntity, QualityScoreEntity, HumanReviewEntity,
    CatalogEntity, CatalogItemEntity, ProcessingJobEntity
)

__all__ = [
    "get_db",
    "init_db",
    "engine",
    "SessionLocal",
    "Base",
    "ProductEntity",
    "ProductVersionEntity",
    "ProductSourceEntity",
    "ProductSpecificationEntity",
    "EvidenceRecordEntity",
    "ValidationRecordEntity",
    "EnrichmentRecordEntity",
    "QualityScoreEntity",
    "HumanReviewEntity",
    "CatalogEntity",
    "CatalogItemEntity",
    "ProcessingJobEntity",
]
