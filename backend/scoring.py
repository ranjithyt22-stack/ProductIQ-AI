"""
Product Quality Score and Deterministic Commerce Readiness Engine for ProductIQ AI.
Calculates 0-100 quality score across 5 core dimensions and determines strict commerce readiness.
"""

from typing import List, Optional
from backend.models import (
    ProductQualityScore, ProductInfo, SpecificationAttribute,
    ValidationResult, CommerceReadinessStatus, MatchStatus, ConflictRecord,
    ConflictStatus, ConflictSeverity
)


def calculate_quality_score(
    product: ProductInfo,
    specifications: List[SpecificationAttribute],
    validations: List[ValidationResult],
    conflicts: Optional[List[ConflictRecord]] = None
) -> ProductQualityScore:
    """
    Computes Product Quality Score (0-100) across 5 core dimensions:
    Completeness, Extraction Quality, Validation Quality, Evidence Coverage, and Consistency.
    Determines deterministic Commerce Readiness Status.
    Strictly gates READY_FOR_COMMERCE if unresolved CRITICAL or HIGH conflicts exist.
    """
    # Dimension 1: Completeness (0-100)
    req_fields = [product.product_name, product.manufacturer, product.product_code, product.category, product.description]
    present_req = sum(1 for f in req_fields if f and str(f).strip().lower() not in ["null", "none", "not found", ""])
    completeness_score = int((present_req / len(req_fields)) * 100)

    # Dimension 2: Extraction Quality (0-100)
    if specifications:
        valid_specs = [s for s in specifications if s.value and str(s.value).strip().lower() not in ["null", "none", "not found"]]
        if valid_specs:
            avg_conf = sum(s.confidence for s in valid_specs) / len(valid_specs)
            extraction_score = int(avg_conf)
        else:
            extraction_score = 0
    else:
        extraction_score = 0

    # Dimension 3: Validation Quality (0-100)
    if validations:
        pass_count = sum(1 for v in validations if v.status == "PASS")
        validation_score = int((pass_count / len(validations)) * 100)
    else:
        validation_score = 100

    # Dimension 4: Evidence Coverage (0-100)
    if specifications:
        backed_specs = sum(
            1 for s in specifications
            if s.match_status in [MatchStatus.VERIFIED, MatchStatus.PARTIALLY_VERIFIED] and s.evidence
        )
        evidence_score = int((backed_specs / len(specifications)) * 100)
    else:
        evidence_score = 0

    # Dimension 5: Consistency Score (0-100)
    open_conflicts = [c for c in (conflicts or []) if c.status == ConflictStatus.OPEN]
    has_blocking_conflicts = any(c.severity in [ConflictSeverity.CRITICAL, ConflictSeverity.HIGH] for c in open_conflicts)
    has_val_conflicts = any(v.status == "REVIEW" or "Conflict" in v.rule for v in validations)

    fail_or_warning = sum(1 for v in validations if v.status in ["FAIL", "WARNING", "REVIEW"]) + len(open_conflicts)
    consistency_score = max(0, int(100 - (fail_or_warning * 10)))

    # Overall Score (Weighted Average)
    # Weights: Completeness 25%, Extraction 25%, Validation 20%, Evidence 15%, Consistency 15%
    overall = int(
        (completeness_score * 0.25) +
        (extraction_score * 0.25) +
        (validation_score * 0.20) +
        (evidence_score * 0.15) +
        (consistency_score * 0.15)
    )

    # Deterministic Commerce Readiness Evaluation
    all_human_verified = len(specifications) > 0 and all(s.review_status == "human_verified" for s in specifications)

    if not product.product_name or len(specifications) == 0:
        status_category = CommerceReadinessStatus.NOT_READY
    elif has_blocking_conflicts or has_val_conflicts:
        status_category = CommerceReadinessStatus.REVIEW_REQUIRED
    elif all_human_verified and validation_score >= 80:
        status_category = CommerceReadinessStatus.HUMAN_VERIFIED
    elif any(s.review_required for s in specifications) or any(v.status in ["FAIL", "REVIEW"] for v in validations):
        status_category = CommerceReadinessStatus.REVIEW_REQUIRED
    elif overall >= 85 and completeness_score >= 80 and evidence_score >= 70 and validation_score >= 80:
        status_category = CommerceReadinessStatus.READY_FOR_COMMERCE
    elif overall >= 70:
        status_category = CommerceReadinessStatus.REVIEW_REQUIRED
    else:
        status_category = CommerceReadinessStatus.NOT_READY

    return ProductQualityScore(
        overall_score=overall,
        completeness=completeness_score,
        extraction_quality=extraction_score,
        validation_quality=validation_score,
        evidence_coverage=evidence_score,
        consistency=consistency_score,
        status_category=status_category
    )
