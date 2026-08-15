"""
Attribute-Level Confidence Engine for ProductIQ AI.
Provides deterministic, multi-factor scoring based on evidence veracity,
source reliability, normalization success, validation results, and cross-source consensus.
"""

from typing import Optional, Tuple
from backend.models import MatchStatus, SourceReliability


def get_confidence_tier(score: int) -> str:
    """Classifies a numeric 0-100 confidence score into standard industry tiers."""
    if score >= 90:
        return "HIGH"
    elif score >= 70:
        return "MEDIUM"
    elif score >= 50:
        return "LOW"
    return "UNVERIFIED"


def calculate_attribute_confidence(
    val_str: Optional[str],
    unit_str: Optional[str] = None,
    page_num: Optional[int] = None,
    evidence_snippet: str = "",
    evidence_score: float = 0.0,
    match_status: str = MatchStatus.VERIFIED,
    source_reliability: str = SourceReliability.OFFICIAL_DATASHEET,
    has_validation_warning: bool = False,
    is_conflicting: bool = False,
    is_inferred: bool = False,
    review_status: str = "ai_extracted"
) -> int:
    """
    Computes deterministic 0-100 attribute confidence score.
    Applies source reliability weighting, validation penalties, and anti-hallucination bounds.
    """
    # 1. Human verified override
    if review_status == "human_verified":
        return 100

    # 2. Empty / Null value
    if not val_str or str(val_str).strip().lower() in ["null", "none", "not found", "unknown", ""]:
        return 0

    # 3. Complete lack of evidence (anti-hallucination check)
    if match_status == MatchStatus.NOT_FOUND or evidence_score == 0.0 or not evidence_snippet:
        if is_inferred:
            return 35  # AI Inferred attribute
        return 0  # Unbacked hallucination / unverified

    # 4. Multi-factor base calculation
    base_score = 30.0

    # Factor A: Evidence Verification (up to +35 pts)
    if match_status == MatchStatus.VERIFIED or evidence_score >= 0.85:
        base_score += 35.0
    elif match_status == MatchStatus.PARTIALLY_VERIFIED or evidence_score >= 0.60:
        base_score += 20.0
    else:
        base_score += 10.0

    # Factor B: Page Attribution (+10 pts)
    if page_num is not None and page_num > 0:
        base_score += 10.0

    # Factor C: Unit Standardization (+10 pts)
    if unit_str and len(unit_str.strip()) > 0:
        base_score += 10.0

    # Factor D: Validation Integrity (+15 pts or -25 pts)
    if not has_validation_warning:
        base_score += 15.0
    else:
        base_score -= 25.0

    # Factor E: Cross-source conflict penalty (-35 pts)
    if is_conflicting or match_status == MatchStatus.CONFLICTING:
        base_score -= 35.0

    # Factor F: Inferred penalty (-30 pts)
    if is_inferred:
        base_score -= 30.0

    # 5. Apply Source Reliability Multiplier
    source_weight = SourceReliability.WEIGHTS.get(source_reliability, 0.85)
    final_score = int(round(base_score * source_weight))

    # Clamp bounds
    return max(0, min(100, final_score))
