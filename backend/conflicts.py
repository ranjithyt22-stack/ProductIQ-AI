"""
Deterministic Cross-Source Conflict Detection & Resolution Engine for ProductIQ AI.
Performs normalized attribute comparison, unit equivalence conversion, conflict classification,
deterministic severity assignment, dynamic conflict confidence calculation, and recommendation generation.
"""

import re
import uuid
from typing import List, Dict, Any, Optional, Tuple

from backend.models import (
    SpecificationAttribute, ConflictRecord, ConflictSourceInfo,
    ConflictType, ConflictStatus, ConflictSeverity, SourceReliability,
    MatchStatus, ProductInfo
)
from backend.normalization import normalize_unit, convert_unit_equivalences


def _clean_str(val: Any) -> str:
    """Normalizes string for comparison by lowercasing and trimming spaces."""
    if val is None:
        return ""
    return str(val).strip().lower()


def are_values_equivalent(val_a: Any, unit_a: Optional[str], val_b: Any, unit_b: Optional[str]) -> Tuple[bool, str]:
    """
    Determines if two values from different sources are physically/semantically equivalent.
    Checks:
    1. Exact string match (case/space insensitive)
    2. Range format normalization ("1 to 10" == "1-10" == "1 - 10")
    3. Unit conversions (1 MPa == 10 bar, 1000 mm == 1 m, 1000 g == 1 kg, 1 kW == 1000 W)
    Returns: (is_equivalent, reason)
    """
    s_a = _clean_str(val_a)
    s_b = _clean_str(val_b)
    u_a = normalize_unit(unit_a) or _clean_str(unit_a)
    u_b = normalize_unit(unit_b) or _clean_str(unit_b)

    if not s_a and not s_b:
        return True, "Both values empty"
    if not s_a or not s_b:
        return False, "One value missing"

    # Direct match if units are same (or absent) and values are identical
    if s_a == s_b and (u_a == u_b or not u_a or not u_b):
        return True, "Exact match"

    # Normalize range strings
    norm_range_a = re.sub(r"\s*(?:to|-)\s*", " to ", s_a)
    norm_range_b = re.sub(r"\s*(?:to|-)\s*", " to ", s_b)

    if norm_range_a == norm_range_b and (u_a == u_b or not u_a or not u_b):
        return True, "Equivalent range format"

    # Unit Conversion checks
    # Pressure: MPa <-> bar
    if (u_a == "MPa" and u_b == "bar") or (u_a == "bar" and u_b == "MPa"):
        conv_val_a, conv_u_a, _, _ = convert_unit_equivalences(s_a, u_a)
        conv_val_b, conv_u_b, _, _ = convert_unit_equivalences(s_b, u_b)
        if _clean_str(conv_val_a) == _clean_str(conv_val_b):
            return True, f"Unit equivalence ({val_a} {unit_a} == {val_b} {unit_b})"

    # Length: mm <-> m <-> cm
    try:
        if (u_a == "mm" and u_b == "m") or (u_a == "m" and u_b == "mm"):
            num_a = float(re.sub(r"[^\d.-]", "", s_a))
            num_b = float(re.sub(r"[^\d.-]", "", s_b))
            mm_a = num_a if u_a == "mm" else num_a * 1000.0
            mm_b = num_b if u_b == "mm" else num_b * 1000.0
            if abs(mm_a - mm_b) < 1e-3:
                return True, f"Length unit equivalence ({val_a} {unit_a} == {val_b} {unit_b})"

        if (u_a == "cm" and u_b == "mm") or (u_a == "mm" and u_b == "cm"):
            num_a = float(re.sub(r"[^\d.-]", "", s_a))
            num_b = float(re.sub(r"[^\d.-]", "", s_b))
            mm_a = num_a if u_a == "mm" else num_a * 10.0
            mm_b = num_b if u_b == "mm" else num_b * 10.0
            if abs(mm_a - mm_b) < 1e-3:
                return True, f"Length unit equivalence ({val_a} {unit_a} == {val_b} {unit_b})"

        # Weight: kg <-> g
        if (u_a == "kg" and u_b == "g") or (u_a == "g" and u_b == "kg"):
            num_a = float(re.sub(r"[^\d.-]", "", s_a))
            num_b = float(re.sub(r"[^\d.-]", "", s_b))
            g_a = num_a if u_a == "g" else num_a * 1000.0
            g_b = num_b if u_b == "g" else num_b * 1000.0
            if abs(g_a - g_b) < 1e-3:
                return True, f"Mass unit equivalence ({val_a} {unit_a} == {val_b} {unit_b})"

        # Power: kW <-> W
        if (u_a == "kW" and u_b == "W") or (u_a == "W" and u_b == "kW"):
            num_a = float(re.sub(r"[^\d.-]", "", s_a))
            num_b = float(re.sub(r"[^\d.-]", "", s_b))
            w_a = num_a if u_a == "W" else num_a * 1000.0
            w_b = num_b if u_b == "W" else num_b * 1000.0
            if abs(w_a - w_b) < 1e-3:
                return True, f"Power unit equivalence ({val_a} {unit_a} == {val_b} {unit_b})"
    except (ValueError, TypeError):
        pass

    return False, "Values and units differ"


def determine_conflict_severity(attribute_name: str, conflict_type: str) -> str:
    """
    Assigns deterministic severity level:
    CRITICAL: Product identity (SKU, Part #, Manufacturer), safety-critical specifications (Pressure, Voltage, Temperature, Hazardous Area).
    HIGH: Major functional engineering parameters (Bore, Stroke, Load Rating, Speed, Power).
    MEDIUM: Minor technical specifications (Port size, Fluid, Mounting).
    LOW: Formatting or non-essential descriptive details.
    """
    if conflict_type == ConflictType.IDENTITY_CONFLICT:
        return ConflictSeverity.CRITICAL

    attr_low = attribute_name.lower()

    # Safety & Operating Limits
    critical_keywords = [
        "pressure", "voltage", "temperature", "hazardous", "explosion",
        "flammable", "safety", "max limit", "rated voltage", "part number", "product code"
    ]
    if any(kw in attr_low for kw in critical_keywords):
        return ConflictSeverity.CRITICAL

    # Core functional engineering specs
    high_keywords = [
        "bore", "stroke", "dynamic load", "static load", "power", "speed",
        "torque", "flow rate", "accuracy", "resolution", "current", "capacity"
    ]
    if any(kw in attr_low for kw in high_keywords):
        return ConflictSeverity.HIGH

    # Secondary specifications
    medium_keywords = [
        "port", "mounting", "fluid", "material", "seal", "cushioning", "weight", "dimensions", "ip rating"
    ]
    if any(kw in attr_low for kw in medium_keywords):
        return ConflictSeverity.MEDIUM

    return ConflictSeverity.LOW


def calculate_conflict_confidence(
    source_a_rel: str,
    source_b_rel: str,
    ev_score_a: float = 0.9,
    ev_score_b: float = 0.9,
    evidence_status_a: str = MatchStatus.VERIFIED,
    evidence_status_b: str = MatchStatus.VERIFIED
) -> int:
    """
    Computes deterministic confidence score (0-100) for the detected conflict.
    Higher when both sources are authoritative and supported by verified evidence.
    """
    w_a = SourceReliability.WEIGHTS.get(source_a_rel, 0.7)
    w_b = SourceReliability.WEIGHTS.get(source_b_rel, 0.7)

    # Status multipliers
    mult_a = 1.0 if evidence_status_a == MatchStatus.VERIFIED else (0.8 if evidence_status_a == MatchStatus.PARTIALLY_VERIFIED else 0.4)
    mult_b = 1.0 if evidence_status_b == MatchStatus.VERIFIED else (0.8 if evidence_status_b == MatchStatus.PARTIALLY_VERIFIED else 0.4)

    raw_score = ((w_a * mult_a * ev_score_a) + (w_b * mult_b * ev_score_b)) / 2.0 * 100.0
    return int(min(100, max(10, round(raw_score))))


def detect_product_conflicts(
    product_id: str,
    specifications: List[SpecificationAttribute],
    product_info: Optional[ProductInfo] = None,
    user_metadata: Optional[Dict[str, Any]] = None,
    version_id: Optional[str] = None
) -> List[ConflictRecord]:
    """
    Performs comprehensive cross-source conflict detection on product version specifications.
    Groups parameters by normalized name, evaluates multi-source discrepancies, checks
    product identity, and generates structured ConflictRecord items.
    """
    conflicts: List[ConflictRecord] = []

    # 1. Check Product Identity Conflicts (e.g. user-provided vs document-provided SKU/Manufacturer)
    if product_info and user_metadata:
        for field_name in ["product_code", "manufacturer", "product_name"]:
            u_val = user_metadata.get(field_name)
            p_val = getattr(product_info, field_name, None)

            if u_val and p_val and _clean_str(u_val) != _clean_str(p_val):
                # If neither is substring of the other
                if _clean_str(u_val) not in _clean_str(p_val) and _clean_str(p_val) not in _clean_str(u_val):
                    cid = f"conf-{uuid.uuid4().hex[:8]}"
                    src_a = ConflictSourceInfo(
                        name="User Supplied Metadata",
                        source_type="user_input",
                        source_reliability=SourceReliability.USER_INPUT,
                        value=str(u_val),
                        evidence_status=MatchStatus.VERIFIED,
                        confidence=85.0
                    )
                    src_b = ConflictSourceInfo(
                        name="Extracted Document Data",
                        source_type="document",
                        source_reliability=SourceReliability.OFFICIAL_DATASHEET,
                        value=str(p_val),
                        evidence_status=MatchStatus.VERIFIED,
                        confidence=95.0
                    )
                    conf = ConflictRecord(
                        conflict_id=cid,
                        product_id=product_id,
                        version_id=version_id,
                        attribute_name=field_name.replace("_", " ").title(),
                        source_a=src_a,
                        source_b=src_b,
                        value_a=str(u_val),
                        value_b=str(p_val),
                        conflict_type=ConflictType.IDENTITY_CONFLICT,
                        severity=ConflictSeverity.CRITICAL,
                        confidence=92,
                        status=ConflictStatus.OPEN,
                        reason=f"Identity discrepancy on '{field_name}': User specified '{u_val}', whereas source document states '{p_val}'.",
                        recommended_action="Verify against physical product label or manufacturer certificate of conformance.",
                        review_required=True
                    )
                    conflicts.append(conf)

    # 2. Group Specifications by Normalized Attribute Name
    grouped_specs: Dict[str, List[SpecificationAttribute]] = {}
    for spec in specifications:
        norm_key = _clean_str(spec.name)
        if norm_key not in grouped_specs:
            grouped_specs[norm_key] = []
        grouped_specs[norm_key].append(spec)

    # 3. Compare Multi-Source Specifications within each group
    for norm_key, specs_list in grouped_specs.items():
        if len(specs_list) < 2:
            continue

        # Check pairwise across distinct sources
        for i in range(len(specs_list)):
            for j in range(i + 1, len(specs_list)):
                spec_a = specs_list[i]
                spec_b = specs_list[j]

                # Check if from same source (Duplicate attribute) or different sources
                is_same_source = (
                    spec_a.source_name and spec_b.source_name and
                    _clean_str(spec_a.source_name) == _clean_str(spec_b.source_name)
                )

                is_equiv, equiv_reason = are_values_equivalent(
                    spec_a.value, spec_a.unit,
                    spec_b.value, spec_b.unit
                )

                if is_equiv:
                    continue  # Equivalent values, no conflict

                # Determine Conflict Type
                if is_same_source:
                    ctype = ConflictType.DUPLICATE_ATTRIBUTE
                elif spec_a.unit and spec_b.unit and _clean_str(spec_a.unit) != _clean_str(spec_b.unit):
                    ctype = ConflictType.UNIT_MISMATCH
                else:
                    ctype = ConflictType.VALUE_MISMATCH

                severity = determine_conflict_severity(spec_a.name, ctype)
                conf_score = calculate_conflict_confidence(
                    spec_a.source_reliability,
                    spec_b.source_reliability,
                    ev_score_a=(spec_a.confidence / 100.0 if spec_a.confidence else 0.9),
                    ev_score_b=(spec_b.confidence / 100.0 if spec_b.confidence else 0.9),
                    evidence_status_a=spec_a.match_status,
                    evidence_status_b=spec_b.match_status
                )

                src_a_name = spec_a.source_name or "Source A"
                src_b_name = spec_b.source_name or "Source B"
                val_a_disp = f"{spec_a.value} {spec_a.unit or ''}".strip()
                val_b_disp = f"{spec_b.value} {spec_b.unit or ''}".strip()

                reason_msg = (
                    f"Conflict on attribute '{spec_a.name}': {src_a_name} reports '{val_a_disp}', "
                    f"while {src_b_name} reports '{val_b_disp}'. Values are not equivalent."
                )

                if severity == ConflictSeverity.CRITICAL:
                    rec_action = f"Verify against latest manufacturer datasheet or ISO/CE compliance declaration."
                elif severity == ConflictSeverity.HIGH:
                    rec_action = f"Verify against authoritative technical documentation."
                else:
                    rec_action = f"Review source citations and select canonical value."

                cid = f"conf-{uuid.uuid4().hex[:8]}"

                src_a_info = ConflictSourceInfo(
                    source_id=spec_a.source_id,
                    name=src_a_name,
                    source_type=spec_a.source_type or "document",
                    source_reliability=spec_a.source_reliability,
                    value=spec_a.value,
                    raw_value=spec_a.raw_value or spec_a.value,
                    normalized_value=spec_a.normalized_value or spec_a.value,
                    unit=spec_a.unit,
                    page=spec_a.page,
                    evidence_quote=spec_a.evidence or "",
                    evidence_status=spec_a.match_status,
                    confidence=spec_a.confidence
                )

                src_b_info = ConflictSourceInfo(
                    source_id=spec_b.source_id,
                    name=src_b_name,
                    source_type=spec_b.source_type or "document",
                    source_reliability=spec_b.source_reliability,
                    value=spec_b.value,
                    raw_value=spec_b.raw_value or spec_b.value,
                    normalized_value=spec_b.normalized_value or spec_b.value,
                    unit=spec_b.unit,
                    page=spec_b.page,
                    evidence_quote=spec_b.evidence or "",
                    evidence_status=spec_b.match_status,
                    confidence=spec_b.confidence
                )

                conflict_record = ConflictRecord(
                    conflict_id=cid,
                    product_id=product_id,
                    version_id=version_id,
                    attribute_name=spec_a.name,
                    source_a=src_a_info,
                    source_b=src_b_info,
                    source_a_id=spec_a.source_id,
                    source_b_id=spec_b.source_id,
                    value_a=spec_a.value,
                    value_b=spec_b.value,
                    normalized_value_a=spec_a.normalized_value or spec_a.value,
                    normalized_value_b=spec_b.normalized_value or spec_b.value,
                    unit_a=spec_a.unit,
                    unit_b=spec_b.unit,
                    conflict_type=ctype,
                    severity=severity,
                    confidence=conf_score,
                    status=ConflictStatus.OPEN,
                    reason=reason_msg,
                    recommended_action=rec_action,
                    review_required=True
                )

                # Mark both specifications as requiring review and in conflict
                spec_a.match_status = MatchStatus.CONFLICTING
                spec_b.match_status = MatchStatus.CONFLICTING
                spec_a.status = "REVIEW"
                spec_b.status = "REVIEW"
                spec_a.review_required = True
                spec_b.review_required = True
                spec_a.review_reason = reason_msg
                spec_b.review_reason = reason_msg

                conflicts.append(conflict_record)

    return conflicts
