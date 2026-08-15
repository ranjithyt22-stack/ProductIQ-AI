"""
Main Processing Pipeline for ProductIQ AI.
Integrates extraction, transparent normalization, deterministic evidence verification,
anti-hallucination protection, multi-factor confidence scoring, cross-source conflict detection,
validation, explainability record generation, AI enrichment, and quality scoring.
"""

import os
import uuid
from typing import Dict, Any, Tuple, Optional, List

from backend.models import (
    ProductIntelligenceRecord, ProductInfo, SpecificationAttribute,
    ValidationResult, AIEnrichment, ProductQualityScore,
    EvidenceRecord, ExplainabilityRecord, MatchStatus, EvidenceType,
    SourceReliability, CommerceReadinessStatus, ConflictRecord
)
from backend.extraction import extract_pdf_pages, call_ollama_structured_extraction
from backend.normalization import normalize_specification
from backend.validation import validate_product_data
from backend.evidence import isolate_evidence_record
from backend.confidence import calculate_attribute_confidence, get_confidence_tier
from backend.explainability import build_product_explainability
from backend.enrichment import generate_product_enrichment
from backend.scoring import calculate_quality_score
from backend.conflicts import detect_product_conflicts
from backend.ingestion.models import SourceDocument
from backend.ingestion.manager import ingest_sources, IngestionError


def _detect_source_conflicts(spec_objects: List[SpecificationAttribute]) -> List[ValidationResult]:
    """
    Detects conflicting values across different sources for the same attribute.
    Backward-compatible helper that sets specification review status and returns ValidationResults.
    """
    conflicts = detect_product_conflicts(product_id="TEMP-CHECK", specifications=spec_objects)
    results = []
    for c in conflicts:
        results.append(ValidationResult(
            rule="Multi-Source Conflict Check",
            status="REVIEW",
            severity=c.severity,
            message=c.reason,
            field=c.attribute_name
        ))
    return results


def process_product_intelligence(

    pdf_path: Optional[str] = None,
    manufacturer: Optional[str] = None,
    product_name: Optional[str] = None,
    product_code: Optional[str] = None,
    description: Optional[str] = None,
    product_url: Optional[str] = None,
    source_documents: Optional[List[SourceDocument]] = None
) -> Tuple[Optional[ProductIntelligenceRecord], str]:
    """
    Executes end-to-end ProductIQ AI workflow across single or multi-source inputs.
    Strictly grounds all extracted parameters with verbatim evidence, anti-hallucination guards,
    and cross-source conflict detection.
    """
    user_metadata = {
        "manufacturer": manufacturer.strip() if manufacturer else None,
        "product_name": product_name.strip() if product_name else None,
        "product_code": product_code.strip() if product_code else None,
        "description": description.strip() if description else None,
        "product_url": product_url.strip() if product_url else None,
    }

    # Step 1: Ingestion & Text Assembly
    docs: List[SourceDocument] = []
    if source_documents:
        docs = list(source_documents)
    else:
        files_to_ingest = [pdf_path] if pdf_path and os.path.exists(pdf_path) else []
        urls_to_ingest = [product_url] if product_url and product_url.strip() else []
        pasted_text = description if description and description.strip() else None

        if files_to_ingest or urls_to_ingest or pasted_text:
            try:
                docs = ingest_sources(files=files_to_ingest, urls=urls_to_ingest, text=pasted_text)
            except IngestionError as e:
                return None, f"Ingestion Error: {str(e)}"

    raw_pages: List[Dict[str, Any]] = []
    combined_sections: List[str] = []

    for doc in docs:
        if doc.pages:
            raw_pages.extend(doc.pages)
        else:
            raw_pages.append({
                "source_id": doc.source_id,
                "filename": doc.source_name,
                "page": 1,
                "text": doc.content,
                "source_type": doc.source_type,
                "source_uri": doc.source_uri
            })
        combined_sections.append(f"--- SOURCE: {doc.source_name} ({doc.source_type.upper()}) ---\n{doc.content}")

    combined_text = "\n\n".join(combined_sections)

    if not combined_text.strip():
        return None, "Please provide a valid PDF document, web URL, or text description."

    # Generate persistent product ID
    product_id = f"PIQ-{uuid.uuid4().hex[:6].upper()}"

    # Step 2: AI Structured Extraction
    ai_raw, ai_err = call_ollama_structured_extraction(combined_text, user_metadata)
    if ai_err:
        return None, f"AI Extraction Failed: {ai_err}"

    if not ai_raw or not isinstance(ai_raw, dict):
        return None, "AI failed to return structured product data."

    # Step 3: Product Metadata Assembly
    raw_prod = ai_raw.get("product", {})
    if not isinstance(raw_prod, dict):
        raw_prod = {}

    product_info = ProductInfo(
        product_name=user_metadata.get("product_name") or raw_prod.get("product_name"),
        manufacturer=user_metadata.get("manufacturer") or raw_prod.get("manufacturer"),
        product_code=user_metadata.get("product_code") or raw_prod.get("product_code"),
        category=raw_prod.get("category") or "Industrial Equipment",
        description=user_metadata.get("description") or raw_prod.get("description")
    )

    # Step 4: Parse, Normalize, and Evidence-Ground Specifications
    raw_specs = ai_raw.get("specifications", [])
    spec_objects: List[SpecificationAttribute] = []
    evidence_records: List[EvidenceRecord] = []

    # Map primary source reliability
    primary_source = raw_pages[0] if raw_pages else {}
    src_type_str = str(primary_source.get("source_type", "document")).upper()
    if "PDF" in src_type_str or "DOCX" in src_type_str:
        src_reliability = SourceReliability.OFFICIAL_DATASHEET
    elif "URL" in src_type_str or "WEB" in src_type_str:
        src_reliability = SourceReliability.OFFICIAL_WEBSITE
    elif "CSV" in src_type_str or "XLS" in src_type_str:
        src_reliability = SourceReliability.MANUFACTURER_CATALOG
    else:
        src_reliability = SourceReliability.USER_INPUT

    if isinstance(raw_specs, list):
        for raw_s in raw_specs:
            if not isinstance(raw_s, dict):
                continue
            norm_s = normalize_specification(raw_s)

            name = norm_s.get("name", "").strip()
            val = str(norm_s.get("value", "")).strip()

            if not name or not val or val.lower() in ["null", "none"]:
                continue

            unit = norm_s.get("unit")
            orig_val = norm_s.get("original_value")
            raw_val = norm_s.get("raw_value")
            norm_applied = norm_s.get("normalization_applied", False)
            norm_rule = norm_s.get("normalization_rule")
            hint_page = norm_s.get("page")

            # Deterministic evidence verification
            ev_rec = isolate_evidence_record(
                attr_name=name,
                raw_val_str=raw_val,
                normalized_val_str=val,
                unit_str=unit,
                raw_pages=raw_pages,
                hint_page=hint_page,
                source_reliability=src_reliability
            )

            # Assign source metadata
            ev_rec.product_id = product_id
            ev_rec.source_id = primary_source.get("source_id")
            evidence_records.append(ev_rec)

            # Initial Confidence Calculation
            conf = calculate_attribute_confidence(
                val_str=val,
                unit_str=unit,
                page_num=ev_rec.page_number,
                evidence_snippet=ev_rec.quote,
                evidence_score=ev_rec.evidence_confidence,
                match_status=ev_rec.match_status,
                source_reliability=src_reliability
            )

            spec_obj = SpecificationAttribute(
                name=name,
                value=val if ev_rec.match_status != MatchStatus.NOT_FOUND else val,
                unit=unit,
                original_value=orig_val,
                raw_value=raw_val,
                normalized_value=val,
                normalization_applied=norm_applied,
                normalization_rule=norm_rule,
                page=ev_rec.page_number,
                evidence=ev_rec.quote,
                evidence_id=ev_rec.evidence_id,
                evidence_type=ev_rec.evidence_type,
                match_status=ev_rec.match_status,
                confidence=conf,
                confidence_level=get_confidence_tier(conf),
                source_type=primary_source.get("source_type", "document"),
                source_id=primary_source.get("source_id"),
                source_name=primary_source.get("filename", "Source Document"),
                source_uri=primary_source.get("source_uri"),
                source_reliability=src_reliability,
                status="PASS" if ev_rec.match_status in [MatchStatus.VERIFIED, MatchStatus.PARTIALLY_VERIFIED] else "UNVERIFIED",
                review_status="ai_extracted",
                review_required=(ev_rec.match_status == MatchStatus.NOT_FOUND or conf < 70),
                review_reason="Evidence was not found in the supplied sources." if ev_rec.match_status == MatchStatus.NOT_FOUND else None
            )
            spec_objects.append(spec_obj)

    # Step 5: Deterministic Validation Rules
    validations = validate_product_data(product_info, spec_objects, user_metadata)

    # Step 6: Comprehensive Cross-Source Conflict Detection
    conflicts = detect_product_conflicts(
        product_id=product_id,
        specifications=spec_objects,
        product_info=product_info,
        user_metadata=user_metadata
    )

    # Append conflict validations
    for c in conflicts:
        validations.append(ValidationResult(
            rule="Multi-Source Conflict Check",
            status="REVIEW",
            severity=c.severity,
            message=c.reason,
            field=c.attribute_name
        ))

    # Adjust confidence and statuses based on validation results
    for v in validations:
        if v.status in ["WARNING", "FAIL", "REVIEW"]:
            for s in spec_objects:
                if s.name.lower() == v.field.lower():
                    s.status = v.status
                    s.confidence = calculate_attribute_confidence(
                        val_str=s.value,
                        unit_str=s.unit,
                        page_num=s.page,
                        evidence_snippet=s.evidence,
                        evidence_score=0.5,
                        match_status=s.match_status,
                        source_reliability=s.source_reliability,
                        has_validation_warning=True,
                        is_conflicting=(v.status == "REVIEW" or "Conflict" in v.rule)
                    )
                    s.confidence_level = get_confidence_tier(int(s.confidence))

    # Step 7: Explainability Record Assembly
    conflict_fields = [c.attribute_name for c in conflicts]
    explainability_records = build_product_explainability(
        spec_objects,
        validations,
        cross_source_conflicts=conflict_fields
    )

    # Step 8: AI Enrichment Generation
    enrichment = generate_product_enrichment(
        product_info, spec_objects, ai_raw.get("enrichment")
    )

    top_apps = ai_raw.get("applications", [])
    if isinstance(top_apps, list) and top_apps:
        clean_apps = [str(a) for a in top_apps if a and isinstance(a, (str, dict))]
        if clean_apps:
            enrichment.suggested_applications = list(set(enrichment.suggested_applications + clean_apps))

    top_kws = ai_raw.get("keywords", [])
    if isinstance(top_kws, list) and top_kws:
        clean_kws = [str(k) for k in top_kws if k and isinstance(k, (str, dict))]
        if clean_kws:
            enrichment.search_terms = list(set(enrichment.search_terms + clean_kws))

    # Step 9: Product Quality & Commerce Readiness Score Calculation
    quality_score = calculate_quality_score(product_info, spec_objects, validations, conflicts)

    record = ProductIntelligenceRecord(
        product_id=product_id,
        product=product_info,
        specifications=spec_objects,
        validation=validations,
        enrichment=enrichment,
        quality_score=quality_score,
        review_status="ai_extracted",
        raw_sources=raw_pages if raw_pages else [{"filename": "User Input Text", "page": 1, "text": combined_text}],
        evidence_records=evidence_records,
        explainability=explainability_records,
        conflicts=conflicts
    )

    return record, ""
