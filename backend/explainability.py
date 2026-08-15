"""
Explainability & Diagnostic Engine for ProductIQ AI.
Constructs structured, factual explainability records and human-review diagnostic reasons
without exposing LLM chain-of-thought or internal reasoning.
"""

from typing import List, Dict, Any, Optional
from backend.models import (
    SpecificationAttribute, ExplainabilityRecord, ValidationResult,
    MatchStatus, EvidenceType
)
from backend.confidence import get_confidence_tier


def generate_attribute_explainability(
    spec: SpecificationAttribute,
    validations: Optional[List[ValidationResult]] = None,
    cross_source_conflicts: Optional[List[str]] = None
) -> ExplainabilityRecord:
    """
    Generates a comprehensive explainability record detailing exactly how an attribute
    was extracted, verified, normalized, and scored.
    """
    attr_name = spec.name
    final_val = f"{spec.value} {spec.unit}".strip() if spec.unit and spec.value else spec.value
    raw_val = spec.raw_value or spec.original_value or spec.value
    norm_val = spec.normalized_value or spec.value

    # Determine validation status for this attribute
    val_status = spec.status or "PASS"
    val_msgs = []
    if validations:
        for v in validations:
            if v.field and v.field.lower() == attr_name.lower():
                val_msgs.append(v.message)
                if v.status in ["WARNING", "FAIL", "REVIEW"]:
                    val_status = v.status

    # Check cross source status
    is_conflict = False
    if cross_source_conflicts and attr_name.lower() in [c.lower() for c in cross_source_conflicts]:
        is_conflict = True
        cross_source_status = "CONFLICT"
    elif spec.evidence_type == EvidenceType.MULTI_SOURCE:
        cross_source_status = "AGREEMENT"
    else:
        cross_source_status = "SINGLE_SOURCE"

    # Normalization status
    norm_status = "SUCCESS" if spec.normalization_applied else "UNCHANGED"
    if not spec.value or spec.value.lower() in ["null", "none"]:
        norm_status = "FAILED"

    # Review requirement & Diagnostic Reasons
    review_req = False
    reasons = []

    if spec.review_status == "human_verified":
        review_req = False
        final_status = "HUMAN_VERIFIED"
    elif spec.match_status == MatchStatus.NOT_FOUND or spec.evidence_type == EvidenceType.UNVERIFIED:
        review_req = True
        reasons.append("Evidence was not found in the supplied sources.")
        final_status = "UNVERIFIED"
    elif is_conflict:
        review_req = True
        reasons.append("Multiple sources contain conflicting values for this specification.")
        final_status = "REVIEW_REQUIRED"
    elif val_status in ["WARNING", "FAIL"]:
        review_req = True
        if val_msgs:
            reasons.extend(val_msgs)
        else:
            reasons.append("Attribute triggered engineering validation rule warning.")
        final_status = "REVIEW_REQUIRED"
    elif spec.confidence < 70:
        review_req = True
        reasons.append(f"Confidence score ({int(spec.confidence)}%) is below the high-reliability threshold (70%).")
        final_status = "REVIEW_REQUIRED"
    else:
        review_req = False
        final_status = "VERIFIED"

    review_reason_str = " | ".join(reasons) if reasons else None
    conf_level = get_confidence_tier(int(spec.confidence))

    # Synchronize review flag back to spec
    spec.review_required = review_req
    spec.review_reason = review_reason_str
    spec.confidence_level = conf_level

    return ExplainabilityRecord(
        attribute_name=attr_name,
        final_value=final_val,
        raw_value=raw_val,
        normalized_value=norm_val,
        source=spec.source_name or "Datasheet",
        page=spec.page,
        evidence=spec.evidence,
        evidence_status=spec.match_status,
        evidence_type=spec.evidence_type,
        normalization_status=norm_status,
        normalization_rule=spec.normalization_rule,
        validation_status=val_status,
        cross_source_status=cross_source_status,
        confidence=int(spec.confidence),
        confidence_level=conf_level,
        review_required=review_req,
        review_reason=review_reason_str,
        final_status=final_status
    )


def build_product_explainability(
    specifications: List[SpecificationAttribute],
    validations: List[ValidationResult],
    cross_source_conflicts: Optional[List[str]] = None
) -> List[ExplainabilityRecord]:
    """Builds explainability records for all product specifications."""
    conflicts = list(cross_source_conflicts) if cross_source_conflicts else [v.field for v in validations if "Conflict" in v.rule or v.status == "REVIEW"]
    records = []
    for spec in specifications:
        rec = generate_attribute_explainability(spec, validations, conflicts)
        records.append(rec)
    return records

