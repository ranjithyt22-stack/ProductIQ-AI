"""
Deterministic Evidence Verification Engine for ProductIQ AI.
Provides verifiable, source-backed quote extraction, page location attribution,
and strict anti-hallucination validation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from backend.models import EvidenceRecord, EvidenceType, MatchStatus, SourceReliability


def isolate_evidence_record(
    attr_name: str,
    raw_val_str: Optional[str],
    normalized_val_str: Optional[str],
    unit_str: Optional[str],
    raw_pages: List[Dict[str, Any]],
    hint_page: Optional[int] = None,
    source_reliability: str = SourceReliability.OFFICIAL_DATASHEET,
    is_inferred: bool = False
) -> EvidenceRecord:
    """
    Deterministically searches raw pages to locate verbatim quotes for an extracted attribute.
    Ensures strict anti-hallucination: if no evidence exists, marks status as NOT_FOUND and confidence as 0.0.
    """
    clean_attr = (attr_name or "").strip()
    val_to_check = str(raw_val_str or normalized_val_str or "").strip()
    clean_unit = (unit_str or "").strip()

    # If attribute value is empty or explicitly flagged as null
    if not val_to_check or val_to_check.lower() in ["null", "none", "not found", "unknown", ""]:
        return EvidenceRecord(
            evidence_id=f"ev_none_{abs(hash(clean_attr)) % 100000}",
            attribute_name=clean_attr,
            raw_value=raw_val_str,
            normalized_value=normalized_val_str,
            quote="",
            page_number=None,
            source_location=None,
            evidence_type=EvidenceType.UNVERIFIED,
            match_status=MatchStatus.NOT_FOUND,
            evidence_confidence=0.0
        )

    # Inferred / AI-Enriched attributes are never presented as direct manufacturer evidence
    if is_inferred or source_reliability == SourceReliability.AI_INFERENCE:
        return EvidenceRecord(
            evidence_id=f"ev_ai_{abs(hash(clean_attr)) % 100000}",
            attribute_name=clean_attr,
            raw_value=raw_val_str,
            normalized_value=normalized_val_str,
            quote="AI taxonomy generation from context.",
            page_number=hint_page,
            source_location="AI Inference",
            evidence_type=EvidenceType.AI_ENRICHED,
            match_status=MatchStatus.UNVERIFIED,
            evidence_confidence=0.4
        )

    if not raw_pages:
        return EvidenceRecord(
            evidence_id=f"ev_empty_{abs(hash(clean_attr)) % 100000}",
            attribute_name=clean_attr,
            raw_value=raw_val_str,
            normalized_value=normalized_val_str,
            quote="",
            page_number=None,
            source_location=None,
            evidence_type=EvidenceType.UNVERIFIED,
            match_status=MatchStatus.NOT_FOUND,
            evidence_confidence=0.0
        )

    # Search preferred hint_page first
    pages_to_search = list(raw_pages)
    if hint_page and 1 <= hint_page <= len(raw_pages):
        hint_p = raw_pages[hint_page - 1]
        pages_to_search = [hint_p] + [p for p in raw_pages if p.get("page") != hint_page]

    best_match_page: Optional[int] = None
    best_snippet = ""
    best_score = 0.0
    best_loc = ""
    best_type = EvidenceType.DIRECT
    best_status = MatchStatus.NOT_FOUND

    attr_words = [w.lower() for w in re.split(r"[_\s/-]+", clean_attr) if len(w) > 2]
    val_tokens = [w.lower() for w in re.split(r"[\s,]+", val_to_check) if w.strip()]

    for p in pages_to_search:
        page_num = p.get("page", 1)
        text = p.get("text", "")
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line_idx, line in enumerate(lines):
            line_low = line.lower()

            # Check exact raw value substring or numeric token overlap
            val_in_line = val_to_check.lower() in line_low or any(t in line_low for t in val_tokens if len(t) >= 2)
            unit_in_line = clean_unit.lower() in line_low if clean_unit else True

            # Count attribute keyword overlaps
            attr_matches = sum(1 for w in attr_words if w in line_low)
            attr_ratio = (attr_matches / len(attr_words)) if attr_words else 0.5

            if val_in_line and attr_matches > 0:
                # Strong exact match (Attribute Name + Value)
                score = 0.9 + (0.1 if (unit_in_line and clean_unit) else 0.05)
                if score > best_score:
                    best_score = score
                    best_match_page = page_num
                    best_snippet = line
                    best_loc = f"Page {page_num}, Line {line_idx + 1}"
                    best_type = EvidenceType.TABLE if ("|" in line or "\t" in line or ":" in line) else EvidenceType.DIRECT
                    best_status = MatchStatus.VERIFIED
                    break
            elif val_in_line and unit_in_line and clean_unit:
                # Value + Unit match
                score = 0.75
                if score > best_score:
                    best_score = score
                    best_match_page = page_num
                    best_snippet = line
                    best_loc = f"Page {page_num}, Line {line_idx + 1}"
                    best_type = EvidenceType.DIRECT
                    best_status = MatchStatus.PARTIALLY_VERIFIED
            elif attr_matches == len(attr_words) and len(attr_words) > 0:
                # Attribute label match only
                score = 0.55
                if score > best_score:
                    best_score = score
                    best_match_page = page_num
                    best_snippet = line
                    best_loc = f"Page {page_num}, Line {line_idx + 1}"
                    best_type = EvidenceType.DIRECT
                    best_status = MatchStatus.PARTIALLY_VERIFIED

        if best_score >= 0.95:
            break

    # If evidence found with sufficient certainty
    if best_score >= 0.70 and best_snippet:
        return EvidenceRecord(
            evidence_id=f"ev_{abs(hash(clean_attr + best_snippet)) % 1000000:06d}",
            attribute_name=clean_attr,
            raw_value=raw_val_str,
            normalized_value=normalized_val_str,
            quote=best_snippet,
            page_number=best_match_page,
            source_location=best_loc,
            evidence_type=best_type,
            match_status=best_status,
            evidence_confidence=round(best_score, 2)
        )

    # ANTI-HALLUCINATION TRIGGER:
    # If the LLM claimed a value but no evidence was found in the text
    return EvidenceRecord(
        evidence_id=f"ev_unverified_{abs(hash(clean_attr)) % 1000000:06d}",
        attribute_name=clean_attr,
        raw_value=raw_val_str,
        normalized_value=normalized_val_str,
        quote="",
        page_number=None,
        source_location=None,
        evidence_type=EvidenceType.UNVERIFIED,
        match_status=MatchStatus.NOT_FOUND,
        evidence_confidence=0.0
    )


def isolate_evidence(
    attr_name: str,
    val_str: str,
    unit_str: Optional[str],
    raw_pages: List[Dict[str, Any]],
    hint_page: Optional[int] = None
) -> Tuple[Optional[int], str, float]:
    """
    Backward-compatible tuple interface for isolate_evidence.
    Returns: (page_number, evidence_text, evidence_match_score)
    """
    rec = isolate_evidence_record(
        attr_name=attr_name,
        raw_val_str=val_str,
        normalized_val_str=val_str,
        unit_str=unit_str,
        raw_pages=raw_pages,
        hint_page=hint_page
    )
    return rec.page_number, rec.quote or "Evidence text could not be precisely isolated.", rec.evidence_confidence
