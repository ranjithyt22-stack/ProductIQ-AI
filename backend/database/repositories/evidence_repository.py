"""
Evidence repository for ProductIQ AI.
Handles verbatim evidence quote indexing and citation queries.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import EvidenceRecordEntity


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_evidence_id(self, evidence_id: str) -> Optional[EvidenceRecordEntity]:
        """Retrieves evidence item by ID."""
        return self.db.query(EvidenceRecordEntity).filter(EvidenceRecordEntity.evidence_id == evidence_id).first()

    def get_by_spec_id(self, spec_id: str) -> Optional[EvidenceRecordEntity]:
        """Retrieves evidence attached to a specific specification parameter."""
        return self.db.query(EvidenceRecordEntity).filter(EvidenceRecordEntity.spec_id == spec_id).first()

    def get_by_source_id(self, source_id: str) -> List[EvidenceRecordEntity]:
        """Retrieves all evidence citations extracted from a specific document source."""
        return self.db.query(EvidenceRecordEntity).filter(EvidenceRecordEntity.source_id == source_id).all()

    def get_by_product_id(self, product_id: str) -> List[EvidenceRecordEntity]:
        """Retrieves all evidence items attached to a product."""
        return self.db.query(EvidenceRecordEntity).filter(EvidenceRecordEntity.product_id == product_id).all()

    def get_by_version_id(self, version_id: str) -> List[EvidenceRecordEntity]:
        """Retrieves all evidence items for a specific product version."""
        return self.db.query(EvidenceRecordEntity).filter(EvidenceRecordEntity.version_id == version_id).all()

