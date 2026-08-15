"""
SQLAlchemy ORM Entity models for ProductIQ AI.
Represents products, versions, multi-source provenance, technical specifications,
verbatim evidence, validations, AI enrichment, quality scores, human reviews, and catalog items.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index, Boolean
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base


def _utcnow() -> datetime:
    return datetime.utcnow()


class ProductEntity(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(64), unique=True, nullable=False, index=True)
    manufacturer = Column(String(255), nullable=True, index=True)
    product_name = Column(String(255), nullable=True, index=True)
    product_code = Column(String(128), nullable=True, index=True)
    category = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(64), default="ACTIVE", nullable=False)
    quality_score = Column(Integer, default=0, nullable=False)
    commerce_readiness = Column(String(64), default="REQUIRES MANUAL REVIEW", nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    versions = relationship("ProductVersionEntity", back_populates="product", cascade="all, delete-orphan", order_by="ProductVersionEntity.version_number.desc()")
    sources = relationship("ProductSourceEntity", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "manufacturer": self.manufacturer,
            "product_name": self.product_name,
            "product_code": self.product_code,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "quality_score": self.quality_score,
            "commerce_readiness": self.commerce_readiness,
            "version_count": len(self.versions) if self.versions else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductVersionEntity(Base):
    __tablename__ = "product_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    manufacturer = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    product_code = Column(String(128), nullable=True)
    category = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    quality_score = Column(Integer, default=0, nullable=False)
    commerce_readiness = Column(String(64), default="REQUIRES MANUAL REVIEW", nullable=False)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    product = relationship("ProductEntity", back_populates="versions")
    specifications = relationship("ProductSpecificationEntity", back_populates="version", cascade="all, delete-orphan")
    validations = relationship("ValidationRecordEntity", back_populates="version", cascade="all, delete-orphan")
    enrichment = relationship("EnrichmentRecordEntity", back_populates="version", uselist=False, cascade="all, delete-orphan")
    quality_breakdown = relationship("QualityScoreEntity", back_populates="version", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("HumanReviewEntity", back_populates="version", cascade="all, delete-orphan")
    conflicts = relationship("ConflictRecordEntity", back_populates="version", cascade="all, delete-orphan")
    audits = relationship("ReviewAuditEntity", back_populates="version", cascade="all, delete-orphan")


    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version_id": self.version_id,
            "product_id": self.product_id,
            "version_number": self.version_number,
            "manufacturer": self.manufacturer,
            "product_name": self.product_name,
            "product_code": self.product_code,
            "category": self.category,
            "description": self.description,
            "quality_score": self.quality_score,
            "commerce_readiness": self.commerce_readiness,
            "change_summary": self.change_summary,
            "specification_count": len(self.specifications) if self.specifications else 0,
            "validation_count": len(self.validations) if self.validations else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductSourceEntity(Base):
    __tablename__ = "product_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=True, index=True)
    version_id = Column(String(64), nullable=True, index=True)
    source_type = Column(String(32), nullable=False, index=True)  # PDF, URL, DOCX, CSV, XLSX, TXT, MD, IMAGE, TEXT
    source_name = Column(String(255), nullable=False)
    source_uri = Column(String(1024), nullable=True)
    source_hash = Column(String(64), nullable=True)
    content_preview = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    product = relationship("ProductEntity", back_populates="sources")

    def to_dict(self) -> Dict[str, Any]:
        meta = {}
        if self.metadata_json:
            try:
                meta = json.loads(self.metadata_json)
            except Exception:
                meta = {}
        return {
            "id": self.id,
            "source_id": self.source_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "source_uri": self.source_uri,
            "source_hash": self.source_hash,
            "content_preview": self.content_preview,
            "metadata": meta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductSpecificationEntity(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spec_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(255), nullable=False, index=True)
    raw_value = Column(String(512), nullable=True)
    normalized_value = Column(String(512), nullable=True)
    unit = Column(String(64), nullable=True)
    normalization_applied = Column(Boolean, default=False, nullable=False)
    normalization_rule = Column(String(128), nullable=True)
    source_id = Column(String(64), nullable=True, index=True)
    source_name = Column(String(255), nullable=True)
    source_reliability = Column(String(64), default="OFFICIAL_DATASHEET", nullable=False)
    page_number = Column(Integer, nullable=True)
    evidence_id = Column(String(64), nullable=True)
    evidence_type = Column(String(32), default="DIRECT", nullable=False)
    match_status = Column(String(32), default="VERIFIED", nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    confidence_level = Column(String(32), default="HIGH", nullable=False)
    validation_status = Column(String(32), default="PASS", nullable=False)
    review_status = Column(String(32), default="ai_extracted", nullable=False)
    review_required = Column(Boolean, default=False, nullable=False)
    review_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="specifications")
    evidence = relationship("EvidenceRecordEntity", back_populates="specification", uselist=False, cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "spec_id": self.spec_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "name": self.attribute_name,
            "attribute_name": self.attribute_name,
            "raw_value": self.raw_value,
            "value": self.normalized_value or self.raw_value,
            "normalized_value": self.normalized_value,
            "unit": self.unit,
            "normalization_applied": self.normalization_applied,
            "normalization_rule": self.normalization_rule,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_reliability": self.source_reliability,
            "page": self.page_number,
            "page_number": self.page_number,
            "evidence_id": self.evidence_id,
            "evidence": self.evidence.verbatim_quote if self.evidence else "",
            "evidence_type": self.evidence_type,
            "match_status": self.match_status,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "status": self.validation_status,
            "validation_status": self.validation_status,
            "review_status": self.review_status,
            "review_required": self.review_required,
            "review_reason": self.review_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EvidenceRecordEntity(Base):
    __tablename__ = "evidence_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), nullable=True, index=True)
    version_id = Column(String(64), nullable=True, index=True)
    spec_id = Column(String(64), ForeignKey("product_specifications.spec_id", ondelete="CASCADE"), nullable=True, index=True)
    attribute_name = Column(String(255), nullable=True)
    raw_value = Column(String(512), nullable=True)
    normalized_value = Column(String(512), nullable=True)
    source_id = Column(String(64), nullable=True, index=True)
    source_name = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    source_location = Column(String(255), nullable=True)
    verbatim_quote = Column(Text, nullable=False)
    evidence_type = Column(String(32), default="DIRECT", nullable=False)
    match_status = Column(String(32), default="VERIFIED", nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    specification = relationship("ProductSpecificationEntity", back_populates="evidence")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "spec_id": self.spec_id,
            "attribute_name": self.attribute_name,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "page_number": self.page_number,
            "source_location": self.source_location,
            "verbatim_quote": self.verbatim_quote,
            "quote": self.verbatim_quote,
            "evidence_type": self.evidence_type,
            "match_status": self.match_status,
            "confidence_score": self.confidence_score,
            "evidence_confidence": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }



class ValidationRecordEntity(Base):
    __tablename__ = "validation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    validation_id = Column(String(64), unique=True, nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    status = Column(String(32), default="PASS", nullable=False)  # PASS, WARNING, FAIL, REVIEW
    severity = Column(String(32), default="INFO", nullable=False)  # INFO, LOW, MEDIUM, HIGH
    message = Column(Text, nullable=False)
    field_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="validations")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "validation_id": self.validation_id,
            "version_id": self.version_id,
            "rule": self.rule_name,
            "rule_name": self.rule_name,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "field": self.field_name,
            "field_name": self.field_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EnrichmentRecordEntity(Base):
    __tablename__ = "enrichment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enrichment_id = Column(String(64), unique=True, nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    search_terms_json = Column(Text, default="[]", nullable=False)
    category_path_json = Column(Text, default="[]", nullable=False)
    suggested_applications_json = Column(Text, default="[]", nullable=False)
    search_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="enrichment")

    def to_dict(self) -> Dict[str, Any]:
        try:
            kws = json.loads(self.search_terms_json)
        except Exception:
            kws = []
        try:
            cat_path = json.loads(self.category_path_json)
        except Exception:
            cat_path = []
        try:
            apps = json.loads(self.suggested_applications_json)
        except Exception:
            apps = []
        return {
            "id": self.id,
            "enrichment_id": self.enrichment_id,
            "version_id": self.version_id,
            "search_terms": kws,
            "category_path": cat_path,
            "suggested_applications": apps,
            "search_summary": self.search_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class QualityScoreEntity(Base):
    __tablename__ = "quality_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    score_id = Column(String(64), unique=True, nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    overall_score = Column(Integer, default=0, nullable=False)
    completeness = Column(Integer, default=0, nullable=False)
    extraction_quality = Column(Integer, default=0, nullable=False)
    validation_quality = Column(Integer, default=0, nullable=False)
    evidence_coverage = Column(Integer, default=0, nullable=False)
    consistency = Column(Integer, default=0, nullable=False)
    status_category = Column(String(64), default="REQUIRES MANUAL REVIEW", nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="quality_breakdown")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "score_id": self.score_id,
            "version_id": self.version_id,
            "overall_score": self.overall_score,
            "completeness": self.completeness,
            "extraction_quality": self.extraction_quality,
            "validation_quality": self.validation_quality,
            "evidence_coverage": self.evidence_coverage,
            "consistency": self.consistency,
            "status_category": self.status_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class HumanReviewEntity(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(255), nullable=False)
    original_value = Column(String(512), nullable=True)
    reviewed_value = Column(String(512), nullable=False)
    reviewed_unit = Column(String(64), nullable=True)
    verification_note = Column(Text, nullable=True)
    status = Column(String(64), default="human_verified", nullable=False)  # human_verified, rejected, accepted
    reviewer_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="reviews")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "review_id": self.review_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "attribute_name": self.attribute_name,
            "original_value": self.original_value,
            "reviewed_value": self.reviewed_value,
            "reviewed_unit": self.reviewed_unit,
            "verification_note": self.verification_note,
            "status": self.status,
            "reviewer_id": self.reviewer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CatalogEntity(Base):
    __tablename__ = "catalogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    catalog_id = Column(String(64), unique=True, nullable=False, index=True)
    catalog_name = Column(String(255), nullable=True)
    processing_status = Column(String(64), default="COMPLETED", nullable=False)
    total_products = Column(Integer, default=0, nullable=False)
    processed_products = Column(Integer, default=0, nullable=False)
    ready_products = Column(Integer, default=0, nullable=False)
    review_required_products = Column(Integer, default=0, nullable=False)
    failed_products = Column(Integer, default=0, nullable=False)
    average_quality_score = Column(Float, default=0.0, nullable=False)
    average_evidence_coverage = Column(Float, default=0.0, nullable=False)
    validation_pass_rate = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    items = relationship("CatalogItemEntity", back_populates="catalog", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "catalog_id": self.catalog_id,
            "catalog_name": self.catalog_name,
            "processing_status": self.processing_status,
            "total_products": self.total_products,
            "processed_products": self.processed_products,
            "ready_products": self.ready_products,
            "review_required_products": self.review_required_products,
            "failed_products": self.failed_products,
            "average_quality_score": self.average_quality_score,
            "average_evidence_coverage": self.average_evidence_coverage,
            "validation_pass_rate": self.validation_pass_rate,
            "product_count": len(self.items) if self.items else 0,
            "products": [item.to_dict() for item in self.items] if self.items else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CatalogItemEntity(Base):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    catalog_id = Column(String(64), ForeignKey("catalogs.catalog_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    product_name = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    product_code = Column(String(128), nullable=True)
    category = Column(String(255), nullable=True)
    quality_score = Column(Integer, default=0, nullable=False)
    readiness_status = Column(String(64), default="REQUIRES MANUAL REVIEW", nullable=False)
    processing_status = Column(String(64), default="COMPLETED", nullable=False)
    error_message = Column(Text, nullable=True)
    record_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    catalog = relationship("CatalogEntity", back_populates="items")

    def to_dict(self) -> Dict[str, Any]:
        rec = None
        if self.record_json:
            try:
                rec = json.loads(self.record_json)
            except Exception:
                rec = None
        return {
            "id": self.id,
            "catalog_id": self.catalog_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "manufacturer": self.manufacturer,
            "product_code": self.product_code,
            "category": self.category,
            "quality_score": self.quality_score,
            "readiness_status": self.readiness_status,
            "status": self.processing_status,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
            "record": rec,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProcessingJobEntity(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), unique=True, nullable=False, index=True)
    job_type = Column(String(64), nullable=False, index=True)  # SINGLE_PRODUCT, CATALOG_BATCH, URL_INGESTION
    status = Column(String(64), default="QUEUED", nullable=False, index=True)  # QUEUED, PROCESSING, COMPLETED, FAILED
    input_payload_json = Column(Text, nullable=True)
    result_summary_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConflictRecordEntity(Base):
    __tablename__ = "conflict_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conflict_id = Column(String(64), unique=True, nullable=False, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(255), nullable=False, index=True)

    source_a_id = Column(String(64), nullable=True)
    source_b_id = Column(String(64), nullable=True)
    source_a_name = Column(String(255), nullable=True)
    source_b_name = Column(String(255), nullable=True)
    source_a_type = Column(String(64), default="document", nullable=False)
    source_b_type = Column(String(64), default="document", nullable=False)
    source_a_reliability = Column(String(64), default="OFFICIAL_DATASHEET", nullable=False)
    source_b_reliability = Column(String(64), default="OFFICIAL_WEBSITE", nullable=False)

    value_a = Column(String(512), nullable=True)
    value_b = Column(String(512), nullable=True)
    raw_value_a = Column(String(512), nullable=True)
    raw_value_b = Column(String(512), nullable=True)
    normalized_value_a = Column(String(512), nullable=True)
    normalized_value_b = Column(String(512), nullable=True)
    unit_a = Column(String(64), nullable=True)
    unit_b = Column(String(64), nullable=True)
    page_a = Column(Integer, nullable=True)
    page_b = Column(Integer, nullable=True)
    evidence_a = Column(Text, nullable=True)
    evidence_b = Column(Text, nullable=True)
    evidence_status_a = Column(String(32), default="VERIFIED", nullable=False)
    evidence_status_b = Column(String(32), default="VERIFIED", nullable=False)
    confidence_a = Column(Float, default=90.0, nullable=False)
    confidence_b = Column(Float, default=90.0, nullable=False)

    conflict_type = Column(String(64), default="VALUE_MISMATCH", nullable=False)
    severity = Column(String(32), default="HIGH", nullable=False)
    confidence = Column(Integer, default=90, nullable=False)
    status = Column(String(32), default="OPEN", nullable=False)  # OPEN, UNDER_REVIEW, RESOLVED, DISMISSED
    reason = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    review_required = Column(Boolean, default=True, nullable=False)

    resolved_by = Column(String(128), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_action = Column(String(64), nullable=True)
    resolution_value = Column(String(512), nullable=True)
    resolution_unit = Column(String(64), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="conflicts")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conflict_id": self.conflict_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "attribute_name": self.attribute_name,
            "source_a": {
                "source_id": self.source_a_id,
                "name": self.source_a_name or "Source A",
                "source_type": self.source_a_type,
                "source_reliability": self.source_a_reliability,
                "value": self.value_a,
                "raw_value": self.raw_value_a,
                "normalized_value": self.normalized_value_a,
                "unit": self.unit_a,
                "page": self.page_a,
                "evidence_quote": self.evidence_a or "",
                "evidence_status": self.evidence_status_a,
                "confidence": self.confidence_a,
            },
            "source_b": {
                "source_id": self.source_b_id,
                "name": self.source_b_name or "Source B",
                "source_type": self.source_b_type,
                "source_reliability": self.source_b_reliability,
                "value": self.value_b,
                "raw_value": self.raw_value_b,
                "normalized_value": self.normalized_value_b,
                "unit": self.unit_b,
                "page": self.page_b,
                "evidence_quote": self.evidence_b or "",
                "evidence_status": self.evidence_status_b,
                "confidence": self.confidence_b,
            },
            "source_a_id": self.source_a_id,
            "source_b_id": self.source_b_id,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "normalized_value_a": self.normalized_value_a,
            "normalized_value_b": self.normalized_value_b,
            "unit_a": self.unit_a,
            "unit_b": self.unit_b,
            "conflict_type": self.conflict_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status,
            "reason": self.reason,
            "recommended_action": self.recommended_action,
            "review_required": self.review_required,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_action": self.resolution_action,
            "resolution_value": self.resolution_value,
            "resolution_unit": self.resolution_unit,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReviewAuditEntity(Base):
    __tablename__ = "review_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(64), unique=True, nullable=False, index=True)
    conflict_id = Column(String(64), nullable=True, index=True)
    review_id = Column(String(64), nullable=True, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    version_id = Column(String(64), ForeignKey("product_versions.version_id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(255), nullable=False)
    reviewer = Column(String(128), default="Reviewer 1", nullable=False)
    action = Column(String(64), nullable=False)  # USE_SOURCE_A, USE_SOURCE_B, ENTER_CORRECT_VALUE, KEEP_BOTH, MARK_UNRESOLVED, DISMISS_CONFLICT
    old_status = Column(String(32), default="OPEN", nullable=False)
    new_status = Column(String(32), default="RESOLVED", nullable=False)
    old_value = Column(String(512), nullable=True)
    new_value = Column(String(512), nullable=True)
    selected_source = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    version = relationship("ProductVersionEntity", back_populates="audits")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "audit_id": self.audit_id,
            "conflict_id": self.conflict_id,
            "review_id": self.review_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "attribute_name": self.attribute_name,
            "reviewer": self.reviewer,
            "action": self.action,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "selected_source": self.selected_source,
            "reason": self.reason,
            "notes": self.notes,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EvaluationRunEntity(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String(64), unique=True, nullable=False, index=True)
    dataset_name = Column(String(128), default="Industrial Benchmark v1", nullable=False)
    dataset_version = Column(String(32), default="1.0", nullable=False)
    model_provider = Column(String(64), default="Ollama", nullable=False)
    model_name = Column(String(128), default="llama3.2:3b", nullable=False)
    model_version = Column(String(64), default="latest", nullable=False)
    status = Column(String(32), default="COMPLETED", nullable=False)  # QUEUED, RUNNING, COMPLETED, FAILED
    quality_gate_status = Column(String(32), default="PASS", nullable=False)  # PASS, FAIL, WARNING
    total_products = Column(Integer, default=0, nullable=False)
    total_attributes = Column(Integer, default=0, nullable=False)
    overall_score = Column(Float, default=0.0, nullable=False)

    # Core Metric Summaries
    extraction_precision = Column(Float, default=0.0, nullable=False)
    extraction_recall = Column(Float, default=0.0, nullable=False)
    extraction_f1 = Column(Float, default=0.0, nullable=False)
    value_accuracy = Column(Float, default=0.0, nullable=False)
    unit_accuracy = Column(Float, default=0.0, nullable=False)
    evidence_coverage = Column(Float, default=0.0, nullable=False)
    hallucination_rate = Column(Float, default=0.0, nullable=False)
    validation_f1 = Column(Float, default=0.0, nullable=False)
    conflict_f1 = Column(Float, default=0.0, nullable=False)
    commerce_readiness_accuracy = Column(Float, default=0.0, nullable=False)
    confidence_calibration_score = Column(Float, default=0.0, nullable=False)

    summary_json = Column(Text, nullable=True)
    confusion_matrix_json = Column(Text, nullable=True)
    calibration_data_json = Column(Text, nullable=True)

    started_at = Column(DateTime, default=_utcnow, nullable=False)
    completed_at = Column(DateTime, default=_utcnow, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    product_results = relationship("EvaluationProductResultEntity", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship("EvaluationMetricEntity", back_populates="run", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "dataset_name": self.dataset_name,
            "dataset_version": self.dataset_version,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "status": self.status,
            "quality_gate_status": self.quality_gate_status,
            "total_products": self.total_products,
            "total_attributes": self.total_attributes,
            "overall_score": round(self.overall_score, 1),
            "extraction_precision": round(self.extraction_precision, 1),
            "extraction_recall": round(self.extraction_recall, 1),
            "extraction_f1": round(self.extraction_f1, 1),
            "value_accuracy": round(self.value_accuracy, 1),
            "unit_accuracy": round(self.unit_accuracy, 1),
            "evidence_coverage": round(self.evidence_coverage, 1),
            "hallucination_rate": round(self.hallucination_rate, 1),
            "validation_f1": round(self.validation_f1, 1),
            "conflict_f1": round(self.conflict_f1, 1),
            "commerce_readiness_accuracy": round(self.commerce_readiness_accuracy, 1),
            "confidence_calibration_score": round(self.confidence_calibration_score, 1),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EvaluationProductResultEntity(Base):
    __tablename__ = "evaluation_product_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(String(64), unique=True, nullable=False, index=True)
    evaluation_id = Column(String(64), ForeignKey("evaluation_runs.evaluation_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(64), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=False)

    tp_count = Column(Integer, default=0, nullable=False)
    fp_count = Column(Integer, default=0, nullable=False)
    fn_count = Column(Integer, default=0, nullable=False)
    extraction_precision = Column(Float, default=0.0, nullable=False)
    extraction_recall = Column(Float, default=0.0, nullable=False)
    extraction_f1 = Column(Float, default=0.0, nullable=False)
    value_accuracy = Column(Float, default=0.0, nullable=False)
    unit_accuracy = Column(Float, default=0.0, nullable=False)
    evidence_coverage = Column(Float, default=0.0, nullable=False)
    hallucination_rate = Column(Float, default=0.0, nullable=False)
    validation_f1 = Column(Float, default=0.0, nullable=False)
    conflict_f1 = Column(Float, default=0.0, nullable=False)
    commerce_readiness_correct = Column(Boolean, default=True, nullable=False)
    expected_readiness = Column(String(64), nullable=True)
    actual_readiness = Column(String(64), nullable=True)

    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    run = relationship("EvaluationRunEntity", back_populates="product_results")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "result_id": self.result_id,
            "evaluation_id": self.evaluation_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "category": self.category,
            "tp_count": self.tp_count,
            "fp_count": self.fp_count,
            "fn_count": self.fn_count,
            "extraction_precision": round(self.extraction_precision, 1),
            "extraction_recall": round(self.extraction_recall, 1),
            "extraction_f1": round(self.extraction_f1, 1),
            "value_accuracy": round(self.value_accuracy, 1),
            "unit_accuracy": round(self.unit_accuracy, 1),
            "evidence_coverage": round(self.evidence_coverage, 1),
            "hallucination_rate": round(self.hallucination_rate, 1),
            "validation_f1": round(self.validation_f1, 1),
            "conflict_f1": round(self.conflict_f1, 1),
            "commerce_readiness_correct": self.commerce_readiness_correct,
            "expected_readiness": self.expected_readiness,
            "actual_readiness": self.actual_readiness,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EvaluationMetricEntity(Base):
    __tablename__ = "evaluation_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(String(64), unique=True, nullable=False, index=True)
    evaluation_id = Column(String(64), ForeignKey("evaluation_runs.evaluation_id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(128), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_category = Column(String(64), nullable=False)  # EXTRACTION, ACCURACY, EVIDENCE, VALIDATION, CONFLICT, COMMERCE
    threshold_value = Column(Float, nullable=True)
    passed_gate = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    run = relationship("EvaluationRunEntity", back_populates="metrics")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "metric_id": self.metric_id,
            "evaluation_id": self.evaluation_id,
            "metric_name": self.metric_name,
            "metric_value": round(self.metric_value, 2),
            "metric_category": self.metric_category,
            "threshold_value": self.threshold_value,
            "passed_gate": self.passed_gate,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelRegistryEntity(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(64), unique=True, nullable=False, index=True)
    model_name = Column(String(128), nullable=False)
    version = Column(String(32), default="1.0", nullable=False)
    provider = Column(String(64), default="Ollama", nullable=False)
    runtime = Column(String(64), default="Local", nullable=False)
    status = Column(String(32), default="Production", nullable=False)  # Development, Testing, Approved, Production, Deprecated
    overall_score = Column(Float, default=0.0, nullable=False)
    extraction_f1 = Column(Float, default=0.0, nullable=False)
    hallucination_rate = Column(Float, default=0.0, nullable=False)
    evidence_coverage = Column(Float, default=0.0, nullable=False)
    description = Column(Text, nullable=True)
    parameters_count = Column(String(32), default="3.2B", nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "version": self.version,
            "provider": self.provider,
            "runtime": self.runtime,
            "status": self.status,
            "overall_score": round(self.overall_score, 1),
            "extraction_f1": round(self.extraction_f1, 1),
            "hallucination_rate": round(self.hallucination_rate, 1),
            "evidence_coverage": round(self.evidence_coverage, 1),
            "description": self.description,
            "parameters_count": self.parameters_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PromptRegistryEntity(Base):
    __tablename__ = "prompt_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(String(64), unique=True, nullable=False, index=True)
    prompt_name = Column(String(128), nullable=False)
    prompt_type = Column(String(64), default="EXTRACTION", nullable=False)  # EXTRACTION, ENRICHMENT, VALIDATION, CONFLICT
    version = Column(String(32), default="1.0", nullable=False)
    purpose = Column(String(255), nullable=True)
    template_text = Column(Text, nullable=False)
    input_variables_json = Column(Text, default="[]", nullable=True)
    status = Column(String(32), default="Production", nullable=False)  # Draft, Testing, Production, Archived
    author = Column(String(128), default="ProductIQ System", nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "prompt_name": self.prompt_name,
            "prompt_type": self.prompt_type,
            "version": self.version,
            "purpose": self.purpose,
            "template_text": self.template_text,
            "status": self.status,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }



