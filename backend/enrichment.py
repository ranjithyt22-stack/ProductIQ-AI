"""
AI Enrichment module for ProductIQ AI.
Generates search terms, category paths, suggested applications, and search summaries.
Ensures clear separation between document-backed facts and AI enrichment.
"""

from typing import List, Dict, Any, Optional
from backend.models import AIEnrichment, ProductInfo, SpecificationAttribute


def generate_product_enrichment(
    product: ProductInfo,
    specifications: List[SpecificationAttribute],
    llm_enrichment_data: Optional[Dict[str, Any]] = None
) -> AIEnrichment:
    """
    Constructs and sanitizes AI enrichment metadata from LLM output with deterministic fallback rules.
    """
    enrichment = AIEnrichment()

    # Sanitization helpers to ensure arrays of strings
    def sanitize_string_list(raw_item: Any) -> List[str]:
        if not raw_item:
            return []
        if isinstance(raw_item, list):
            result = []
            for item in raw_item:
                if isinstance(item, str) and item.strip():
                    result.append(item.strip())
                elif isinstance(item, dict):
                    # Handle case if LLM returned dict like {"name": "...", "value": "..."}
                    val = item.get("name") or item.get("value") or item.get("term")
                    if val and str(val).strip():
                        result.append(str(val).strip())
            return result
        if isinstance(raw_item, str) and raw_item.strip():
            return [raw_item.strip()]
        return []

    # Try extracting LLM enrichment if present
    if llm_enrichment_data and isinstance(llm_enrichment_data, dict):
        enrichment.search_terms = sanitize_string_list(llm_enrichment_data.get("search_terms") or llm_enrichment_data.get("keywords"))
        enrichment.category_path = sanitize_string_list(llm_enrichment_data.get("category_path"))
        enrichment.suggested_applications = sanitize_string_list(llm_enrichment_data.get("suggested_applications") or llm_enrichment_data.get("applications"))

    # Fallback / Deterministic Enhancement based strictly on confirmed source facts
    prod_name = product.product_name or "Industrial Product"
    mfr = product.manufacturer or ""
    cat = product.category or "Industrial Equipment"
    code = product.product_code or ""

    # Category Path Defaulting if empty
    if not enrichment.category_path:
        cat_low = cat.lower()
        if "pneumatic" in cat_low or "cylinder" in cat_low or "actuator" in cat_low:
            enrichment.category_path = ["Industrial Equipment", "Pneumatics", "Actuators", cat.title()]
        elif "valve" in cat_low:
            enrichment.category_path = ["Industrial Equipment", "Fluid Power", "Valves", cat.title()]
        elif "sensor" in cat_low:
            enrichment.category_path = ["Industrial Equipment", "Automation & Sensors", cat.title()]
        else:
            enrichment.category_path = ["Industrial Equipment", "General Components", cat.title()]

    # Search Terms Generation
    if not enrichment.search_terms:
        base_terms = [prod_name, f"{mfr} {prod_name}".strip(), code, cat]
        for spec in specifications[:4]:
            if spec.value and spec.unit:
                base_terms.append(f"{spec.value} {spec.unit} {cat}".strip())
            elif spec.value:
                base_terms.append(f"{spec.name} {spec.value}".strip())
        enrichment.search_terms = [t for t in dict.fromkeys(base_terms) if t]

    # Search Summary Generation
    key_specs_str = ", ".join([f"{s.name}: {s.value} {s.unit or ''}".strip() for s in specifications[:5] if s.value])
    summary_parts = []
    if mfr:
        summary_parts.append(f"Manufactured by {mfr}.")
    if prod_name:
        summary_parts.append(f"Product: {prod_name} ({code}).")
    if key_specs_str:
        summary_parts.append(f"Key Specifications: {key_specs_str}.")

    enrichment.search_summary = " ".join(summary_parts) if summary_parts else f"Industrial catalog entry for {prod_name}."

    return enrichment
