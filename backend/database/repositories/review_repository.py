"""
Human review repository for ProductIQ AI.
Handles audit logging of human-in-the-loop overrides, conflict resolutions, verifications, and approvals.
"""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import HumanReviewEntity, ReviewAuditEntity


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def record_review(
        self,
        product_id: str,
        version_id: str,
        attribute_name: str,
        reviewed_value: str,
        original_value: Optional[str] = None,
        reviewed_unit: Optional[str] = None,
        verification_note: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        status: str = "human_verified"
    ) -> HumanReviewEntity:
        """Records an immutable human review audit log entry."""
        review_id = f"rev_{uuid.uuid4().hex[:10]}"
        entity = HumanReviewEntity(
            review_id=review_id,
            product_id=product_id,
            version_id=version_id,
            attribute_name=attribute_name,
            original_value=original_value,
            reviewed_value=reviewed_value,
            reviewed_unit=reviewed_unit,
            verification_note=verification_note,
            reviewer_id=reviewer_id,
            status=status
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_id(self, review_id: str) -> Optional[HumanReviewEntity]:
        """Retrieves single review by review_id."""
        return self.db.query(HumanReviewEntity).filter(HumanReviewEntity.review_id == review_id).first()

    def list_reviews(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[HumanReviewEntity]:
        """Lists reviews across all products with pagination."""
        query = self.db.query(HumanReviewEntity)
        if status:
            query = query.filter(HumanReviewEntity.status == status)
        return query.order_by(HumanReviewEntity.created_at.desc()).offset(offset).limit(limit).all()

    def get_by_product(self, product_id: str) -> List[HumanReviewEntity]:
        """Retrieves complete human review history for a product."""
        return (
            self.db.query(HumanReviewEntity)
            .filter(HumanReviewEntity.product_id == product_id)
            .order_by(HumanReviewEntity.created_at.desc())
            .all()
        )

    def get_by_version(self, version_id: str) -> List[HumanReviewEntity]:
        """Retrieves reviews for a specific version."""
        return (
            self.db.query(HumanReviewEntity)
            .filter(HumanReviewEntity.version_id == version_id)
            .order_by(HumanReviewEntity.created_at.desc())
            .all()
        )

    def record_audit(
        self,
        product_id: str,
        version_id: str,
        attribute_name: str,
        reviewer: str,
        action: str,
        old_status: str,
        new_status: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        selected_source: Optional[str] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        conflict_id: Optional[str] = None,
        review_id: Optional[str] = None
    ) -> ReviewAuditEntity:
        """Records an immutable review resolution audit log entry."""
        audit_id = f"aud_{uuid.uuid4().hex[:10]}"
        entity = ReviewAuditEntity(
            audit_id=audit_id,
            conflict_id=conflict_id,
            review_id=review_id,
            product_id=product_id,
            version_id=version_id,
            attribute_name=attribute_name,
            reviewer=reviewer,
            action=action,
            old_status=old_status,
            new_status=new_status,
            old_value=old_value,
            new_value=new_value,
            selected_source=selected_source,
            reason=reason,
            notes=notes
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_audits_by_product_id(self, product_id: str) -> List[ReviewAuditEntity]:
        """Retrieves immutable resolution audits for a product."""
        return (
            self.db.query(ReviewAuditEntity)
            .filter(ReviewAuditEntity.product_id == product_id)
            .order_by(ReviewAuditEntity.created_at.desc())
            .all()
        )

    def get_audits_by_conflict_id(self, conflict_id: str) -> List[ReviewAuditEntity]:
        """Retrieves audits for a specific conflict."""
        return (
            self.db.query(ReviewAuditEntity)
            .filter(ReviewAuditEntity.conflict_id == conflict_id)
            .order_by(ReviewAuditEntity.created_at.desc())
            .all()
        )

    def list_audits(self, limit: int = 50, offset: int = 0) -> List[ReviewAuditEntity]:
        """Lists global review audits."""
        return (
            self.db.query(ReviewAuditEntity)
            .order_by(ReviewAuditEntity.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
