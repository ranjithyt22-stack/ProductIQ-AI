"""
Specification repository for ProductIQ AI.
Handles storage, retrieval, and updating of normalized technical specifications.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import ProductSpecificationEntity


class SpecificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_version(self, version_id: str) -> List[ProductSpecificationEntity]:
        """Retrieves all specifications belonging to a specific product version."""
        return (
            self.db.query(ProductSpecificationEntity)
            .filter(ProductSpecificationEntity.version_id == version_id)
            .all()
        )

    def get_by_attribute_name(self, version_id: str, attribute_name: str) -> Optional[ProductSpecificationEntity]:
        """Retrieves a single specification by attribute name within a version."""
        return (
            self.db.query(ProductSpecificationEntity)
            .filter(
                ProductSpecificationEntity.version_id == version_id,
                ProductSpecificationEntity.attribute_name.ilike(attribute_name)
            )
            .first()
        )

    def update_specification_value(
        self,
        version_id: str,
        attribute_name: str,
        reviewed_value: str,
        reviewed_unit: Optional[str] = None,
        review_status: str = "human_verified"
    ) -> Optional[ProductSpecificationEntity]:
        """Applies a human review override directly to a specification entity."""
        spec = self.get_by_attribute_name(version_id, attribute_name)
        if spec:
            spec.normalized_value = reviewed_value
            if reviewed_unit:
                spec.unit = reviewed_unit
            spec.review_status = review_status
            spec.confidence = 100.0
            self.db.flush()
        return spec
