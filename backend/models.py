"""
Data models and schema helpers for ProductIQ AI.
Includes single-product intelligence records, evidence-grounded schemas,
explainability records, cross-source conflict models, human review audit trail,
and scalable catalog data models.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


class CatalogProcessingStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class EvidenceType:
    DIRECT = "DIRECT"
    TABLE = "TABLE"
    MULTI_SOURCE = "MULTI_SOURCE"
    AI_ENRICHED = "AI_ENRICHED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"


class MatchStatus:
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICTING = "CONFLICTING"
    UNVERIFIED = "UNVERIFIED"


class SourceReliability:
    OFFICIAL_DATASHEET = "OFFICIAL_DATASHEET"
    OFFICIAL_WEBSITE = "OFFICIAL_WEBSITE"
    MANUFACTURER_CATALOG = "MANUFACTURER_CATALOG"
    DISTRIBUTOR = "DISTRIBUTOR"
    THIRD_PARTY = "THIRD_PARTY"
    USER_INPUT = "USER_INPUT"
    AI_INFERENCE = "AI_INFERENCE"

    WEIGHTS = {
        OFFICIAL_DATASHEET: 1.0,
        OFFICIAL_WEBSITE: 0.95,
        MANUFACTURER_CATALOG: 0.90,
        DISTRIBUTOR: 0.75,
        THIRD_PARTY: 0.60,
        USER_INPUT: 0.50,
        AI_INFERENCE: 0.30,
    }


class CommerceReadinessStatus:
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    READY_FOR_COMMERCE = "READY_FOR_COMMERCE"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"


class ConflictType:
    VALUE_MISMATCH = "VALUE_MISMATCH"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    MISSING_VALUE = "MISSING_VALUE"
    DUPLICATE_ATTRIBUTE = "DUPLICATE_ATTRIBUTE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    CATEGORY_CONFLICT = "CATEGORY_CONFLICT"


class ConflictStatus:
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ConflictSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConflictResolutionAction:
    USE_SOURCE_A = "USE_SOURCE_A"
    USE_SOURCE_B = "USE_SOURCE_B"
    ENTER_CORRECT_VALUE = "ENTER_CORRECT_VALUE"
    KEEP_BOTH = "KEEP_BOTH"
    MARK_UNRESOLVED = "MARK_UNRESOLVED"
    DISMISS_CONFLICT = "DISMISS_CONFLICT"


@dataclass
class ProductInfo:
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None
    product_code: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceRecord:
    evidence_id: str
    product_id: Optional[str] = None
    version_id: Optional[str] = None
    spec_id: Optional[str] = None
    attribute_name: Optional[str] = None
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    page_number: Optional[int] = None
    source_location: Optional[str] = None
    verbatim_quote: str = ""
    quote: str = ""
    evidence_type: str = EvidenceType.DIRECT
    match_status: str = MatchStatus.VERIFIED
    confidence_score: float = 1.0
    evidence_confidence: float = 1.0
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.quote and not self.verbatim_quote:
            self.verbatim_quote = self.quote
        elif self.verbatim_quote and not self.quote:
            self.quote = self.verbatim_quote

        if self.evidence_confidence != 1.0 and self.confidence_score == 1.0:
            self.confidence_score = self.evidence_confidence
        elif self.confidence_score != 1.0 and self.evidence_confidence == 1.0:
            self.evidence_confidence = self.confidence_score

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



@dataclass
class SpecificationAttribute:
    name: str
    value: str
    unit: Optional[str] = None
    original_value: Optional[str] = None
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    normalization_applied: bool = False
    normalization_rule: Optional[str] = None
    page: Optional[int] = None
    evidence: Optional[str] = None
    evidence_id: Optional[str] = None
    evidence_type: str = EvidenceType.DIRECT
    match_status: str = MatchStatus.VERIFIED
    confidence: float = 95.0
    confidence_level: str = "HIGH"
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    source_uri: Optional[str] = None
    source_reliability: str = SourceReliability.OFFICIAL_DATASHEET
    status: str = "PASS"  # PASS, WARNING, FAIL, REVIEW, UNVERIFIED
    review_status: str = "ai_extracted"  # ai_extracted, human_verified, rejected, edited
    review_required: bool = False
    review_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplainabilityRecord:
    attribute_name: str
    final_value: str
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    evidence: str = ""
    evidence_status: str = MatchStatus.VERIFIED
    evidence_type: str = EvidenceType.DIRECT
    normalization_status: str = "SUCCESS"
    normalization_rule: Optional[str] = None
    validation_status: str = "PASS"
    cross_source_status: str = "AGREEMENT"
    confidence: int = 0
    confidence_level: str = "HIGH"
    review_required: bool = False
    review_reason: Optional[str] = None
    final_status: str = "VERIFIED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    rule: str
    status: str  # PASS, WARNING, FAIL, REVIEW
    severity: str  # INFO, LOW, MEDIUM, HIGH
    message: str
    field: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AIEnrichment:
    search_terms: List[str] = field(default_factory=list)
    category_path: List[str] = field(default_factory=list)
    suggested_applications: List[str] = field(default_factory=list)
    search_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductQualityScore:
    overall_score: int = 0
    completeness: int = 0
    extraction_quality: int = 0
    validation_quality: int = 0
    evidence_coverage: int = 0
    consistency: int = 0
    status_category: str = CommerceReadinessStatus.REVIEW_REQUIRED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConflictSourceInfo:
    source_id: Optional[str] = None
    name: str = ""
    source_type: str = "document"
    source_reliability: str = SourceReliability.OFFICIAL_DATASHEET
    value: str = ""
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    unit: Optional[str] = None
    page: Optional[int] = None
    evidence_quote: str = ""
    evidence_status: str = MatchStatus.VERIFIED
    confidence: float = 90.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConflictRecord:
    conflict_id: str
    product_id: str
    version_id: Optional[str] = None
    attribute_name: str = ""
    source_a: ConflictSourceInfo = field(default_factory=ConflictSourceInfo)
    source_b: ConflictSourceInfo = field(default_factory=ConflictSourceInfo)
    source_a_id: Optional[str] = None
    source_b_id: Optional[str] = None
    value_a: Optional[str] = None
    value_b: Optional[str] = None
    normalized_value_a: Optional[str] = None
    normalized_value_b: Optional[str] = None
    unit_a: Optional[str] = None
    unit_b: Optional[str] = None
    conflict_type: str = ConflictType.VALUE_MISMATCH
    severity: str = ConflictSeverity.HIGH
    confidence: int = 90
    status: str = ConflictStatus.OPEN
    reason: str = ""
    recommended_action: str = ""
    review_required: bool = True
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    resolution_action: Optional[str] = None
    resolution_value: Optional[str] = None
    resolution_unit: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "product_id": self.product_id,
            "version_id": self.version_id,
            "attribute_name": self.attribute_name,
            "source_a": self.source_a.to_dict() if hasattr(self.source_a, "to_dict") else self.source_a,
            "source_b": self.source_b.to_dict() if hasattr(self.source_b, "to_dict") else self.source_b,
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
            "resolved_at": self.resolved_at,
            "resolution_action": self.resolution_action,
            "resolution_value": self.resolution_value,
            "resolution_unit": self.resolution_unit,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ReviewAuditRecord:
    audit_id: str
    conflict_id: Optional[str] = None
    review_id: Optional[str] = None
    product_id: str = ""
    version_id: Optional[str] = None
    attribute_name: str = ""
    reviewer: str = "Reviewer 1"
    action: str = ConflictResolutionAction.USE_SOURCE_A
    old_status: str = ConflictStatus.OPEN
    new_status: str = ConflictStatus.RESOLVED
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    selected_source: Optional[str] = None
    reason: str = ""
    notes: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductIntelligenceRecord:
    product_id: str
    product: ProductInfo
    specifications: List[SpecificationAttribute] = field(default_factory=list)
    validation: List[ValidationResult] = field(default_factory=list)
    enrichment: AIEnrichment = field(default_factory=AIEnrichment)
    quality_score: ProductQualityScore = field(default_factory=ProductQualityScore)
    review_status: str = "ai_extracted"
    raw_sources: List[Dict[str, Any]] = field(default_factory=list)
    evidence_records: List[EvidenceRecord] = field(default_factory=list)
    explainability: List[ExplainabilityRecord] = field(default_factory=list)
    conflicts: List[ConflictRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product": self.product.to_dict(),
            "specifications": [s.to_dict() for s in self.specifications],
            "validation": [v.to_dict() for v in self.validation],
            "enrichment": self.enrichment.to_dict(),
            "quality_score": self.quality_score.to_dict(),
            "review_status": self.review_status,
            "raw_sources": self.raw_sources,
            "evidence_records": [e.to_dict() for e in self.evidence_records],
            "explainability": [x.to_dict() for x in self.explainability],
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


# ==============================================================================
# CATALOG ENGINE DATA STRUCTURES
# ==============================================================================

@dataclass
class CatalogProduct:
    product_id: str
    product_name: str
    source_id: Optional[str] = None
    manufacturer: Optional[str] = None
    product_code: Optional[str] = None
    category: Optional[str] = None
    quality_score: int = 0
    readiness_status: str = CommerceReadinessStatus.REVIEW_REQUIRED
    validation_status: str = "PASS"
    evidence_coverage: int = 100
    conflict_count: int = 0
    critical_conflict_count: int = 0
    status: str = CatalogProcessingStatus.COMPLETED
    error_message: Optional[str] = None
    record: Optional[ProductIntelligenceRecord] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.record:
            d["record"] = self.record.to_dict()
        return d


@dataclass
class CatalogResult:
    catalog_id: str
    processing_status: str = CatalogProcessingStatus.COMPLETED
    total_products: int = 0
    processed_products: int = 0
    ready_products: int = 0
    review_required_products: int = 0
    failed_products: int = 0
    average_quality_score: float = 0.0
    average_evidence_coverage: float = 0.0
    validation_pass_rate: float = 0.0
    products_with_conflicts: int = 0
    open_conflicts: int = 0
    resolved_conflicts: int = 0
    critical_conflicts: int = 0
    high_conflicts: int = 0
    products: List[CatalogProduct] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "processing_status": self.processing_status,
            "total_products": self.total_products,
            "processed_products": self.processed_products,
            "ready_products": self.ready_products,
            "review_required_products": self.review_required_products,
            "failed_products": self.failed_products,
            "average_quality_score": self.average_quality_score,
            "average_evidence_coverage": self.average_evidence_coverage,
            "validation_pass_rate": self.validation_pass_rate,
            "products_with_conflicts": self.products_with_conflicts,
            "open_conflicts": self.open_conflicts,
            "resolved_conflicts": self.resolved_conflicts,
            "critical_conflicts": self.critical_conflicts,
            "high_conflicts": self.high_conflicts,
            "products": [p.to_dict() for p in self.products]
        }
