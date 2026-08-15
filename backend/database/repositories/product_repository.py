"""
Product and Version repository for ProductIQ AI.
Handles product lifecycle, version creation, version diffing, and complete lineage graph assembly.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from backend.database.models import (
    ProductEntity, ProductVersionEntity, ProductSpecificationEntity,
    EvidenceRecordEntity, ValidationRecordEntity, EnrichmentRecordEntity,
    QualityScoreEntity, HumanReviewEntity, ProductSourceEntity,
    ConflictRecordEntity, ReviewAuditEntity
)
from backend.models import ProductIntelligenceRecord, ConflictRecord



class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: str) -> Optional[ProductEntity]:
        """Retrieves a product by its unique business ID."""
        return self.db.query(ProductEntity).filter(ProductEntity.product_id == product_id).first()

    def list_products(
        self,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        readiness: Optional[str] = None
    ) -> List[ProductEntity]:
        """Lists products with optional keyword search and readiness filters."""
        query = self.db.query(ProductEntity)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ProductEntity.product_name.ilike(pattern),
                    ProductEntity.manufacturer.ilike(pattern),
                    ProductEntity.product_code.ilike(pattern),
                    ProductEntity.product_id.ilike(pattern),
                )
            )
        if readiness and readiness.upper() != "ALL":
            query = query.filter(ProductEntity.commerce_readiness == readiness.upper())

        return query.order_by(desc(ProductEntity.updated_at)).offset(offset).limit(limit).all()

    def create_or_update_product(
        self,
        product_id: str,
        manufacturer: Optional[str] = None,
        product_name: Optional[str] = None,
        product_code: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        quality_score: int = 0,
        commerce_readiness: str = "REQUIRES MANUAL REVIEW",
        status: str = "ACTIVE"
    ) -> ProductEntity:
        """Upserts a product entity header."""
        product = self.get_by_product_id(product_id)
        if not product:
            product = ProductEntity(
                product_id=product_id,
                manufacturer=manufacturer,
                product_name=product_name,
                product_code=product_code,
                category=category,
                description=description,
                quality_score=quality_score,
                commerce_readiness=commerce_readiness,
                status=status
            )
            self.db.add(product)
        else:
            if manufacturer:
                product.manufacturer = manufacturer
            if product_name:
                product.product_name = product_name
            if product_code:
                product.product_code = product_code
            if category:
                product.category = category
            if description:
                product.description = description
            product.quality_score = quality_score
            product.commerce_readiness = commerce_readiness
            product.status = status

        self.db.flush()
        return product

    def save_full_record(
        self,
        record: ProductIntelligenceRecord,
        change_summary: str = "Initial AI Analysis"
    ) -> Tuple[ProductEntity, ProductVersionEntity]:
        """
        Saves a full ProductIntelligenceRecord into the persistence layer.
        Creates a new immutable product version, specifications, validations,
        enrichment, evidence, and quality score.
        """
        product_info = record.product
        q_score_val = record.quality_score.overall_score if record.quality_score else 0
        readiness_val = record.quality_score.status_category if record.quality_score else "REQUIRES MANUAL REVIEW"

        # 1. Upsert product header
        product = self.create_or_update_product(
            product_id=record.product_id,
            manufacturer=product_info.manufacturer,
            product_name=product_info.product_name,
            product_code=product_info.product_code,
            category=product_info.category,
            description=product_info.description,
            quality_score=q_score_val,
            commerce_readiness=readiness_val
        )

        # 2. Determine next version number
        existing_versions = self.get_versions(record.product_id)
        next_ver_num = (existing_versions[0].version_number + 1) if existing_versions else 1
        version_id = f"{record.product_id}-v{next_ver_num}"

        # 3. Create ProductVersionEntity
        version = ProductVersionEntity(
            version_id=version_id,
            product_id=record.product_id,
            version_number=next_ver_num,
            manufacturer=product_info.manufacturer,
            product_name=product_info.product_name,
            product_code=product_info.product_code,
            category=product_info.category,
            description=product_info.description,
            quality_score=q_score_val,
            commerce_readiness=readiness_val,
            change_summary=change_summary
        )
        self.db.add(version)
        self.db.flush()

        # 4. Save Ingested Sources
        if record.raw_sources:
            for src in record.raw_sources:
                src_id = src.get("source_id") or f"src_{uuid.uuid4().hex[:8]}"
                src_entity = ProductSourceEntity(
                    source_id=src_id,
                    product_id=record.product_id,
                    version_id=version_id,
                    source_type=src.get("source_type", "document"),
                    source_name=src.get("filename") or src.get("source_name") or "Document",
                    source_uri=src.get("source_uri"),
                    content_preview=src.get("text", "")[:1000] if src.get("text") else None,
                    metadata_json=json.dumps(src.get("metadata", {}))
                )
                self.db.add(src_entity)

        # 5. Save Specifications and Evidence
        for idx, spec in enumerate(record.specifications):
            spec_id = f"{version_id}-spec-{idx+1:03d}"
            ev_id = f"{spec_id}-ev"

            spec_entity = ProductSpecificationEntity(
                spec_id=spec_id,
                product_id=record.product_id,
                version_id=version_id,
                attribute_name=spec.name,
                raw_value=spec.raw_value or spec.original_value or spec.value,
                normalized_value=spec.normalized_value or spec.value,
                unit=spec.unit,
                normalization_applied=spec.normalization_applied,
                normalization_rule=spec.normalization_rule,
                source_id=spec.source_id,
                source_name=spec.source_name,
                source_reliability=spec.source_reliability,
                page_number=spec.page,
                evidence_id=ev_id,
                evidence_type=spec.evidence_type,
                match_status=spec.match_status,
                confidence=spec.confidence,
                confidence_level=spec.confidence_level,
                validation_status=spec.status or "PASS",
                review_status=spec.review_status or "ai_extracted",
                review_required=spec.review_required,
                review_reason=spec.review_reason
            )
            self.db.add(spec_entity)

            # Link Evidence
            if spec.evidence:
                ev_entity = EvidenceRecordEntity(
                    evidence_id=ev_id,
                    product_id=record.product_id,
                    version_id=version_id,
                    spec_id=spec_id,
                    attribute_name=spec.name,
                    raw_value=spec.raw_value or spec.original_value or spec.value,
                    normalized_value=spec.normalized_value or spec.value,
                    source_id=spec.source_id,
                    source_name=spec.source_name,
                    page_number=spec.page,
                    source_location=f"Page {spec.page}" if spec.page else None,
                    verbatim_quote=spec.evidence,
                    evidence_type=spec.evidence_type,
                    match_status=spec.match_status,
                    confidence_score=spec.confidence / 100.0 if spec.confidence else 1.0
                )
                self.db.add(ev_entity)


        # 6. Save Validations
        for v_idx, val in enumerate(record.validation):
            val_id = f"{version_id}-val-{v_idx+1:03d}"
            val_entity = ValidationRecordEntity(
                validation_id=val_id,
                version_id=version_id,
                rule_name=val.rule,
                status=val.status,
                severity=val.severity,
                message=val.message,
                field_name=val.field
            )
            self.db.add(val_entity)

        # 7. Save AI Enrichment
        if record.enrichment:
            enrich_id = f"{version_id}-enrich"
            enrich_entity = EnrichmentRecordEntity(
                enrichment_id=enrich_id,
                version_id=version_id,
                search_terms_json=json.dumps(record.enrichment.search_terms or []),
                category_path_json=json.dumps(record.enrichment.category_path or []),
                suggested_applications_json=json.dumps(record.enrichment.suggested_applications or []),
                search_summary=record.enrichment.search_summary or ""
            )
            self.db.add(enrich_entity)

        # 8. Save Quality Score Breakdown
        if record.quality_score:
            score_id = f"{version_id}-score"
            score_entity = QualityScoreEntity(
                score_id=score_id,
                version_id=version_id,
                overall_score=record.quality_score.overall_score,
                completeness=record.quality_score.completeness,
                extraction_quality=record.quality_score.extraction_quality,
                validation_quality=record.quality_score.validation_quality,
                evidence_coverage=record.quality_score.evidence_coverage,
                consistency=record.quality_score.consistency,
                status_category=record.quality_score.status_category
            )
            self.db.add(score_entity)

        # 9. Save Cross-Source Conflicts
        if record.conflicts:
            for idx, c in enumerate(record.conflicts):
                c_id = c.conflict_id or f"{version_id}-c{idx+1:03d}"
                c_entity = ConflictRecordEntity(
                    conflict_id=c_id,
                    product_id=record.product_id,
                    version_id=version_id,
                    attribute_name=c.attribute_name,
                    source_a_id=c.source_a_id or (c.source_a.source_id if c.source_a else None),
                    source_b_id=c.source_b_id or (c.source_b.source_id if c.source_b else None),
                    source_a_name=c.source_a.name if c.source_a else "Source A",
                    source_b_name=c.source_b.name if c.source_b else "Source B",
                    source_a_type=c.source_a.source_type if c.source_a else "document",
                    source_b_type=c.source_b.source_type if c.source_b else "document",
                    source_a_reliability=c.source_a.source_reliability if c.source_a else "OFFICIAL_DATASHEET",
                    source_b_reliability=c.source_b.source_reliability if c.source_b else "OFFICIAL_WEBSITE",
                    value_a=c.value_a,
                    value_b=c.value_b,
                    raw_value_a=c.source_a.raw_value if c.source_a else c.value_a,
                    raw_value_b=c.source_b.raw_value if c.source_b else c.value_b,
                    normalized_value_a=c.normalized_value_a or (c.source_a.normalized_value if c.source_a else c.value_a),
                    normalized_value_b=c.normalized_value_b or (c.source_b.normalized_value if c.source_b else c.value_b),
                    unit_a=c.unit_a or (c.source_a.unit if c.source_a else None),
                    unit_b=c.unit_b or (c.source_b.unit if c.source_b else None),
                    page_a=c.source_a.page if c.source_a else None,
                    page_b=c.source_b.page if c.source_b else None,
                    evidence_a=c.source_a.evidence_quote if c.source_a else None,
                    evidence_b=c.source_b.evidence_quote if c.source_b else None,
                    evidence_status_a=c.source_a.evidence_status if c.source_a else "VERIFIED",
                    evidence_status_b=c.source_b.evidence_status if c.source_b else "VERIFIED",
                    confidence_a=c.source_a.confidence if c.source_a else 90.0,
                    confidence_b=c.source_b.confidence if c.source_b else 90.0,
                    conflict_type=c.conflict_type,
                    severity=c.severity,
                    confidence=c.confidence,
                    status=c.status,
                    reason=c.reason,
                    recommended_action=c.recommended_action,
                    review_required=c.review_required
                )
                self.db.add(c_entity)

        self.db.commit()
        return product, version

    def create_version_from_resolution(
        self,
        product_id: str,
        attribute_name: str,
        resolved_value: str,
        resolved_unit: Optional[str] = None,
        resolution_action: str = "ENTER_CORRECT_VALUE",
        reviewer: str = "Reviewer 1",
        reason: str = "Human Review Override",
        notes: Optional[str] = None,
        conflict_id: Optional[str] = None
    ) -> Tuple[ProductEntity, ProductVersionEntity]:
        """
        Creates an immutable new product version (e.g. v2) with the updated resolved attribute value,
        recalculates quality and commerce readiness, and records audit trail.
        """
        product = self.get_by_product_id(product_id)
        if not product:
            raise ValueError(f"Product '{product_id}' not found.")

        versions = self.get_versions(product_id)
        latest_ver = versions[0] if versions else None
        next_ver_num = (latest_ver.version_number + 1) if latest_ver else 1
        new_ver_id = f"{product_id}-v{next_ver_num}"

        change_msg = f"Human review resolved '{attribute_name}' ({resolution_action}): set to '{resolved_value} {resolved_unit or ''}'. Reason: {reason}".strip()

        # Create new immutable version
        new_version = ProductVersionEntity(
            version_id=new_ver_id,
            product_id=product_id,
            version_number=next_ver_num,
            manufacturer=latest_ver.manufacturer if latest_ver else product.manufacturer,
            product_name=latest_ver.product_name if latest_ver else product.product_name,
            product_code=latest_ver.product_code if latest_ver else product.product_code,
            category=latest_ver.category if latest_ver else product.category,
            description=latest_ver.description if latest_ver else product.description,
            change_summary=change_msg
        )
        self.db.add(new_version)
        self.db.flush()

        old_val_str = ""

        # Clone and update specifications
        if latest_ver and latest_ver.specifications:
            for idx, old_spec in enumerate(latest_ver.specifications):
                spec_id = f"{new_ver_id}-spec-{idx+1:03d}"
                is_target = old_spec.attribute_name.strip().lower() == attribute_name.strip().lower()

                val = resolved_value if is_target else (old_spec.normalized_value or old_spec.raw_value)
                u = resolved_unit if is_target else old_spec.unit
                rev_status = "human_verified" if is_target else old_spec.review_status
                conf = 100.0 if is_target else old_spec.confidence
                rev_req = False if is_target else old_spec.review_required
                rev_rsn = None if is_target else old_spec.review_reason

                if is_target:
                    old_val_str = f"{old_spec.normalized_value or old_spec.raw_value} {old_spec.unit or ''}".strip()

                new_spec_entity = ProductSpecificationEntity(
                    spec_id=spec_id,
                    product_id=product_id,
                    version_id=new_ver_id,
                    attribute_name=old_spec.attribute_name,
                    raw_value=old_spec.raw_value,
                    normalized_value=val,
                    unit=u,
                    normalization_applied=old_spec.normalization_applied,
                    normalization_rule=old_spec.normalization_rule,
                    source_id=old_spec.source_id,
                    source_name=old_spec.source_name,
                    source_reliability=old_spec.source_reliability,
                    page_number=old_spec.page_number,
                    evidence_id=old_spec.evidence_id,
                    evidence_type=old_spec.evidence_type,
                    match_status=old_spec.match_status,
                    confidence=conf,
                    confidence_level="HIGH" if conf >= 90 else old_spec.confidence_level,
                    validation_status="PASS",
                    review_status=rev_status,
                    review_required=rev_req,
                    review_reason=rev_rsn
                )
                self.db.add(new_spec_entity)

        # Clone validations
        if latest_ver and latest_ver.validations:
            for v_idx, old_val in enumerate(latest_ver.validations):
                val_id = f"{new_ver_id}-val-{v_idx+1:03d}"
                new_val_entity = ValidationRecordEntity(
                    validation_id=val_id,
                    version_id=new_ver_id,
                    rule_name=old_val.rule_name,
                    status=old_val.status if old_val.field_name.lower() != attribute_name.lower() else "PASS",
                    severity=old_val.severity,
                    message=old_val.message if old_val.field_name.lower() != attribute_name.lower() else f"Resolved via Human Review by {reviewer}",
                    field_name=old_val.field_name
                )
                self.db.add(new_val_entity)

        # Re-evaluate Quality Score and Commerce Readiness
        open_blocking_conflicts = (
            self.db.query(ConflictRecordEntity)
            .filter(
                ConflictRecordEntity.product_id == product_id,
                ConflictRecordEntity.status == "OPEN",
                ConflictRecordEntity.severity.in_(["CRITICAL", "HIGH"])
            )
            .count()
        )

        q_score = min(100, max(0, (latest_ver.quality_score if latest_ver else 80) + 5))
        readiness = "READY_FOR_COMMERCE" if open_blocking_conflicts == 0 else "REVIEW_REQUIRED"

        new_version.quality_score = q_score
        new_version.commerce_readiness = readiness
        product.quality_score = q_score
        product.commerce_readiness = readiness

        # Record Human Review audit
        rev_id = f"rev_{uuid.uuid4().hex[:10]}"
        rev_entity = HumanReviewEntity(
            review_id=rev_id,
            product_id=product_id,
            version_id=new_ver_id,
            attribute_name=attribute_name,
            original_value=old_val_str,
            reviewed_value=resolved_value,
            reviewed_unit=resolved_unit,
            verification_note=f"{reason}. {notes or ''}".strip(),
            status="human_verified",
            reviewer_id=reviewer
        )
        self.db.add(rev_entity)

        # Record immutable Review Audit Entity
        audit_id = f"aud_{uuid.uuid4().hex[:10]}"
        audit_entity = ReviewAuditEntity(
            audit_id=audit_id,
            conflict_id=conflict_id,
            review_id=rev_id,
            product_id=product_id,
            version_id=new_ver_id,
            attribute_name=attribute_name,
            reviewer=reviewer,
            action=resolution_action,
            old_status="OPEN",
            new_status="RESOLVED",
            old_value=old_val_str,
            new_value=f"{resolved_value} {resolved_unit or ''}".strip(),
            selected_source=resolution_action,
            reason=reason,
            notes=notes
        )
        self.db.add(audit_entity)

        self.db.commit()
        return product, new_version


    def get_versions(self, product_id: str) -> List[ProductVersionEntity]:
        """Retrieves all versions of a product in descending order."""
        return (
            self.db.query(ProductVersionEntity)
            .filter(ProductVersionEntity.product_id == product_id)
            .order_by(desc(ProductVersionEntity.version_number))
            .all()
        )

    def get_version(self, product_id: str, version_identifier: Any) -> Optional[ProductVersionEntity]:
        """Retrieves a specific version by version_id string or integer version_number."""
        query = self.db.query(ProductVersionEntity).filter(ProductVersionEntity.product_id == product_id)
        if isinstance(version_identifier, int) or (isinstance(version_identifier, str) and version_identifier.isdigit()):
            query = query.filter(ProductVersionEntity.version_number == int(version_identifier))
        else:
            query = query.filter(ProductVersionEntity.version_id == str(version_identifier))
        return query.first()

    def compare_versions(
        self,
        product_id: str,
        v1_ident: Any,
        v2_ident: Any
    ) -> Dict[str, Any]:
        """
        Compares two versions of a product and generates a detailed diff of specifications,
        metadata changes, and quality score evolution.
        """
        v1 = self.get_version(product_id, v1_ident)
        v2 = self.get_version(product_id, v2_ident)

        if not v1 or not v2:
            return {"error": "One or both requested versions not found."}

        # Specs mapping
        v1_specs = {s.attribute_name.lower(): s for s in v1.specifications}
        v2_specs = {s.attribute_name.lower(): s for s in v2.specifications}

        all_keys = set(v1_specs.keys()) | set(v2_specs.keys())
        spec_diffs = []

        for key in sorted(all_keys):
            s1 = v1_specs.get(key)
            s2 = v2_specs.get(key)

            if s1 and not s2:
                spec_diffs.append({
                    "attribute": s1.attribute_name,
                    "change_type": "REMOVED",
                    "v1_value": f"{s1.normalized_value or s1.raw_value} {s1.unit or ''}".strip(),
                    "v2_value": None,
                })
            elif not s1 and s2:
                spec_diffs.append({
                    "attribute": s2.attribute_name,
                    "change_type": "ADDED",
                    "v1_value": None,
                    "v2_value": f"{s2.normalized_value or s2.raw_value} {s2.unit or ''}".strip(),
                })
            else:
                val1 = f"{s1.normalized_value or s1.raw_value} {s1.unit or ''}".strip()
                val2 = f"{s2.normalized_value or s2.raw_value} {s2.unit or ''}".strip()
                if val1 != val2 or s1.validation_status != s2.validation_status:
                    spec_diffs.append({
                        "attribute": s2.attribute_name,
                        "change_type": "MODIFIED",
                        "v1_value": val1,
                        "v2_value": val2,
                        "v1_status": s1.validation_status,
                        "v2_status": s2.validation_status,
                    })
                else:
                    spec_diffs.append({
                        "attribute": s2.attribute_name,
                        "change_type": "UNCHANGED",
                        "v1_value": val1,
                        "v2_value": val2,
                    })

        return {
            "product_id": product_id,
            "v1": {
                "version_id": v1.version_id,
                "version_number": v1.version_number,
                "quality_score": v1.quality_score,
                "commerce_readiness": v1.commerce_readiness,
                "created_at": v1.created_at.isoformat() if v1.created_at else None,
            },
            "v2": {
                "version_id": v2.version_id,
                "version_number": v2.version_number,
                "quality_score": v2.quality_score,
                "commerce_readiness": v2.commerce_readiness,
                "created_at": v2.created_at.isoformat() if v2.created_at else None,
            },
            "metadata_diff": {
                "product_name": {"v1": v1.product_name, "v2": v2.product_name},
                "manufacturer": {"v1": v1.manufacturer, "v2": v2.manufacturer},
                "product_code": {"v1": v1.product_code, "v2": v2.product_code},
                "category": {"v1": v1.category, "v2": v2.category},
            },
            "specification_diffs": spec_diffs
        }

    def get_lineage(self, product_id: str, version_identifier: Optional[Any] = None) -> Dict[str, Any]:
        """
        Builds the complete end-to-end data lineage graph for a product version:
        Product -> Version -> Specification -> Source -> Evidence -> Normalization -> Validation -> Confidence -> Review
        """
        product = self.get_by_product_id(product_id)
        if not product:
            return {"error": f"Product '{product_id}' not found."}

        if version_identifier is not None:
            version = self.get_version(product_id, version_identifier)
        else:
            versions = self.get_versions(product_id)
            version = versions[0] if versions else None

        if not version:
            return {"error": f"No versions available for product '{product_id}'."}

        sources = (
            self.db.query(ProductSourceEntity)
            .filter(ProductSourceEntity.version_id == version.version_id)
            .all()
        )
        source_map = {s.source_id: s.to_dict() for s in sources}

        lineage_specs = []
        for s in version.specifications:
            ev = s.evidence
            src_info = source_map.get(s.source_id, {})
            lineage_specs.append({
                "specification": {
                    "attribute_name": s.attribute_name,
                    "raw_value": s.raw_value,
                    "normalized_value": s.normalized_value,
                    "unit": s.unit,
                },
                "source": {
                    "source_id": s.source_id,
                    "source_name": s.source_name or src_info.get("source_name", "Document"),
                    "source_type": src_info.get("source_type", "document"),
                    "source_reliability": s.source_reliability,
                    "source_uri": src_info.get("source_uri"),
                    "page_number": s.page_number,
                },
                "evidence": {
                    "evidence_id": ev.evidence_id if ev else None,
                    "verbatim_quote": ev.verbatim_quote if ev else "",
                    "quote": ev.verbatim_quote if ev else "",
                    "evidence_type": s.evidence_type,
                    "match_status": s.match_status,
                    "confidence_score": ev.confidence_score if ev else 0.0,
                },
                "normalization": {
                    "applied": s.normalization_applied,
                    "rule": s.normalization_rule,
                    "raw_value": s.raw_value,
                    "normalized_value": s.normalized_value,
                },
                "validation": {
                    "status": s.validation_status,
                    "confidence": s.confidence,
                },
                "confidence": {
                    "score": s.confidence,
                    "level": s.confidence_level,
                },
                "human_review": {
                    "review_status": s.review_status,
                    "review_required": s.review_required,
                    "review_reason": s.review_reason,
                },
                "final_value": f"{s.normalized_value or s.raw_value} {s.unit or ''}".strip()
            })

        return {
            "product": product.to_dict(),
            "version": version.to_dict(),
            "sources": [s.to_dict() for s in sources],
            "lineage_items": lineage_specs,
            "lineage_summary": {
                "total_attributes": len(lineage_specs),
                "backed_by_verbatim_evidence": sum(1 for item in lineage_specs if item["evidence"]["verbatim_quote"]),
                "validation_passed": sum(1 for item in lineage_specs if item["validation"]["status"] == "PASS"),
                "human_verified": sum(1 for item in lineage_specs if item["human_review"]["review_status"] == "human_verified"),
                "requires_review": sum(1 for item in lineage_specs if item["human_review"]["review_required"]),
            }
        }

