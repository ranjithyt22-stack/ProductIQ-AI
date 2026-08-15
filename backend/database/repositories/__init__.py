"""
Repository implementations for ProductIQ AI data access layer.
"""

from backend.database.repositories.product_repository import ProductRepository
from backend.database.repositories.source_repository import SourceRepository
from backend.database.repositories.specification_repository import SpecificationRepository
from backend.database.repositories.evidence_repository import EvidenceRepository
from backend.database.repositories.validation_repository import ValidationRepository
from backend.database.repositories.review_repository import ReviewRepository
from backend.database.repositories.conflict_repository import ConflictRepository
from backend.database.repositories.catalog_repository import CatalogRepository
from backend.database.repositories.job_repository import JobRepository
from backend.database.repositories.evaluation_repository import EvaluationRepository

__all__ = [
    "ProductRepository",
    "SourceRepository",
    "SpecificationRepository",
    "EvidenceRepository",
    "ValidationRepository",
    "ReviewRepository",
    "ConflictRepository",
    "CatalogRepository",
    "JobRepository",
    "EvaluationRepository",
]


