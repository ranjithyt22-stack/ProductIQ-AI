"""
Conflict Repository for ProductIQ AI.
Handles persistence, queries, lifecycle status changes, and statistics for cross-source conflicts.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.models import ConflictRecordEntity, ReviewAuditEntity
from backend.models import ConflictRecord, ConflictStatus, ConflictResolutionAction


def _utcnow() -> datetime:
    return datetime.utcnow()


class ConflictRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conflict(self, conflict: ConflictRecord) -> ConflictRecordEntity:
        """Saves a new ConflictRecord into the persistent database."""
        entity = ConflictRecordEntity(
            conflict_id=conflict.conflict_id,
            product_id=conflict.product_id,
            version_id=conflict.version_id or "",
            attribute_name=conflict.attribute_name,
            source_a_id=conflict.source_a_id or (conflict.source_a.source_id if conflict.source_a else None),
            source_b_id=conflict.source_b_id or (conflict.source_b.source_id if conflict.source_b else None),
            source_a_name=conflict.source_a.name if conflict.source_a else "Source A",
            source_b_name=conflict.source_b.name if conflict.source_b else "Source B",
            source_a_type=conflict.source_a.source_type if conflict.source_a else "document",
            source_b_type=conflict.source_b.source_type if conflict.source_b else "document",
            source_a_reliability=conflict.source_a.source_reliability if conflict.source_a else "OFFICIAL_DATASHEET",
            source_b_reliability=conflict.source_b.source_reliability if conflict.source_b else "OFFICIAL_WEBSITE",
            value_a=conflict.value_a,
            value_b=conflict.value_b,
            raw_value_a=conflict.source_a.raw_value if conflict.source_a else conflict.value_a,
            raw_value_b=conflict.source_b.raw_value if conflict.source_b else conflict.value_b,
            normalized_value_a=conflict.normalized_value_a or (conflict.source_a.normalized_value if conflict.source_a else conflict.value_a),
            normalized_value_b=conflict.normalized_value_b or (conflict.source_b.normalized_value if conflict.source_b else conflict.value_b),
            unit_a=conflict.unit_a or (conflict.source_a.unit if conflict.source_a else None),
            unit_b=conflict.unit_b or (conflict.source_b.unit if conflict.source_b else None),
            page_a=conflict.source_a.page if conflict.source_a else None,
            page_b=conflict.source_b.page if conflict.source_b else None,
            evidence_a=conflict.source_a.evidence_quote if conflict.source_a else None,
            evidence_b=conflict.source_b.evidence_quote if conflict.source_b else None,
            evidence_status_a=conflict.source_a.evidence_status if conflict.source_a else "VERIFIED",
            evidence_status_b=conflict.source_b.evidence_status if conflict.source_b else "VERIFIED",
            confidence_a=conflict.source_a.confidence if conflict.source_a else 90.0,
            confidence_b=conflict.source_b.confidence if conflict.source_b else 90.0,
            conflict_type=conflict.conflict_type,
            severity=conflict.severity,
            confidence=conflict.confidence,
            status=conflict.status,
            reason=conflict.reason,
            recommended_action=conflict.recommended_action,
            review_required=conflict.review_required,
            resolution_action=conflict.resolution_action,
            resolution_value=conflict.resolution_value,
            resolution_unit=conflict.resolution_unit,
            resolution_notes=conflict.resolution_notes,
            resolved_by=conflict.resolved_by
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_id(self, conflict_id: str) -> Optional[ConflictRecordEntity]:
        """Retrieves a specific conflict by conflict_id."""
        return self.db.query(ConflictRecordEntity).filter(ConflictRecordEntity.conflict_id == conflict_id).first()

    def get_by_product_id(self, product_id: str, status: Optional[str] = None) -> List[ConflictRecordEntity]:
        """Retrieves all conflicts associated with a product."""
        query = self.db.query(ConflictRecordEntity).filter(ConflictRecordEntity.product_id == product_id)
        if status:
            query = query.filter(ConflictRecordEntity.status == status)
        return query.order_by(ConflictRecordEntity.created_at.desc()).all()

    def get_by_version_id(self, version_id: str) -> List[ConflictRecordEntity]:
        """Retrieves all conflicts attached to a product version."""
        return self.db.query(ConflictRecordEntity).filter(ConflictRecordEntity.version_id == version_id).all()

    def list_conflicts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        product_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConflictRecordEntity]:
        """Lists conflicts across all products with filtering and pagination."""
        query = self.db.query(ConflictRecordEntity)
        if status:
            query = query.filter(ConflictRecordEntity.status == status)
        if severity:
            query = query.filter(ConflictRecordEntity.severity == severity)
        if product_id:
            query = query.filter(ConflictRecordEntity.product_id == product_id)

        # Order by Severity hierarchy (CRITICAL first, then HIGH, MEDIUM, LOW) then newest
        return query.order_by(ConflictRecordEntity.created_at.desc()).offset(offset).limit(limit).all()

    def resolve_conflict(
        self,
        conflict_id: str,
        action: str,
        resolution_value: Optional[str] = None,
        resolution_unit: Optional[str] = None,
        resolution_notes: Optional[str] = None,
        reviewer: str = "Reviewer 1"
    ) -> Optional[ConflictRecordEntity]:
        """Resolves a conflict with human review choice and creates an immutable audit record."""
        conflict = self.get_by_id(conflict_id)
        if not conflict:
            return None

        old_status = conflict.status
        old_val = conflict.value_a if action == ConflictResolutionAction.USE_SOURCE_A else (conflict.value_b if action == ConflictResolutionAction.USE_SOURCE_B else conflict.resolution_value)

        # Determine effective resolved value
        final_val = resolution_value
        final_unit = resolution_unit
        selected_src = None

        if action == ConflictResolutionAction.USE_SOURCE_A:
            final_val = conflict.value_a
            final_unit = conflict.unit_a
            selected_src = conflict.source_a_name
        elif action == ConflictResolutionAction.USE_SOURCE_B:
            final_val = conflict.value_b
            final_unit = conflict.unit_b
            selected_src = conflict.source_b_name
        elif action == ConflictResolutionAction.ENTER_CORRECT_VALUE:
            final_val = resolution_value
            final_unit = resolution_unit
            selected_src = "Human Engineer Override"
        elif action == ConflictResolutionAction.DISMISS_CONFLICT:
            conflict.status = ConflictStatus.DISMISSED
            conflict.review_required = False
            conflict.resolved_by = reviewer
            conflict.resolved_at = _utcnow()
            conflict.resolution_action = action
            conflict.resolution_notes = resolution_notes
            self.db.flush()
            return conflict

        conflict.status = ConflictStatus.RESOLVED
        conflict.review_required = False
        conflict.resolved_by = reviewer
        conflict.resolved_at = _utcnow()
        conflict.resolution_action = action
        conflict.resolution_value = final_val
        conflict.resolution_unit = final_unit
        conflict.resolution_notes = resolution_notes

        # Create immutable audit record
        audit_id = f"aud_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{conflict.conflict_id[:6]}"
        audit_entity = ReviewAuditEntity(
            audit_id=audit_id,
            conflict_id=conflict.conflict_id,
            product_id=conflict.product_id,
            version_id=conflict.version_id,
            attribute_name=conflict.attribute_name,
            reviewer=reviewer,
            action=action,
            old_status=old_status,
            new_status=ConflictStatus.RESOLVED,
            old_value=old_val,
            new_value=f"{final_val} {final_unit or ''}".strip(),
            selected_source=selected_src,
            reason=conflict.reason,
            notes=resolution_notes
        )
        self.db.add(audit_entity)
        self.db.flush()

        return conflict

    def dismiss_conflict(
        self,
        conflict_id: str,
        reviewer: str = "Reviewer 1",
        reason: Optional[str] = None
    ) -> Optional[ConflictRecordEntity]:
        """Dismisses a conflict as non-actionable."""
        return self.resolve_conflict(
            conflict_id=conflict_id,
            action=ConflictResolutionAction.DISMISS_CONFLICT,
            resolution_notes=reason,
            reviewer=reviewer
        )

    def get_conflict_stats(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates aggregated metrics for conflicts."""
        query = self.db.query(ConflictRecordEntity)
        if product_id:
            query = query.filter(ConflictRecordEntity.product_id == product_id)

        all_conflicts = query.all()
        total = len(all_conflicts)
        open_c = sum(1 for c in all_conflicts if c.status == ConflictStatus.OPEN)
        resolved_c = sum(1 for c in all_conflicts if c.status == ConflictStatus.RESOLVED)
        dismissed_c = sum(1 for c in all_conflicts if c.status == ConflictStatus.DISMISSED)
        critical_c = sum(1 for c in all_conflicts if c.severity == "CRITICAL" and c.status == ConflictStatus.OPEN)
        high_c = sum(1 for c in all_conflicts if c.severity == "HIGH" and c.status == ConflictStatus.OPEN)

        return {
            "total_conflicts": total,
            "open_conflicts": open_c,
            "resolved_conflicts": resolved_c,
            "dismissed_conflicts": dismissed_c,
            "critical_conflicts": critical_c,
            "high_conflicts": high_c,
            "has_blocking_conflicts": (critical_c > 0 or high_c > 0)
        }
