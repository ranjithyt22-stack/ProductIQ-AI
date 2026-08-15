"""
Validation repository for ProductIQ AI.
Handles persistence and query filtering for deterministic validation checks.
"""

from typing import List
from sqlalchemy.orm import Session
from backend.database.models import ValidationRecordEntity


class ValidationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_version(self, version_id: str) -> List[ValidationRecordEntity]:
        """Retrieves all validation checks for a product version."""
        return self.db.query(ValidationRecordEntity).filter(ValidationRecordEntity.version_id == version_id).all()

    def get_issues_by_version(self, version_id: str) -> List[ValidationRecordEntity]:
        """Retrieves only warnings and failures for a product version."""
        return (
            self.db.query(ValidationRecordEntity)
            .filter(
                ValidationRecordEntity.version_id == version_id,
                ValidationRecordEntity.status.in_(["WARNING", "FAIL", "REVIEW"])
            )
            .all()
        )
