"""
Migration utility for ProductIQ AI.
Scans legacy uploads/ directory for existing JSON product intelligence records
and imports them into the persistent relational database without deleting original files.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from backend.database.connection import get_db_context, init_db
from backend.database.repositories.product_repository import ProductRepository
from backend.models import (
    ProductIntelligenceRecord, ProductInfo, SpecificationAttribute,
    ValidationResult, AIEnrichment, ProductQualityScore
)

logger = logging.getLogger("productiq_migration")


def dict_to_record(data: Dict[str, Any]) -> Optional[ProductIntelligenceRecord]:
    """Converts a dictionary into a ProductIntelligenceRecord dataclass instance."""
    try:
        p_raw = data.get("product", {})
        prod_info = ProductInfo(
            product_name=p_raw.get("product_name"),
            manufacturer=p_raw.get("manufacturer"),
            product_code=p_raw.get("product_code"),
            category=p_raw.get("category"),
            description=p_raw.get("description")
        )

        specs = []
        for s in data.get("specifications", []):
            specs.append(SpecificationAttribute(
                name=s.get("name") or s.get("attribute_name", ""),
                value=str(s.get("value") or s.get("normalized_value", "")),
                unit=s.get("unit"),
                original_value=s.get("original_value") or s.get("raw_value"),
                page=s.get("page") or s.get("page_number"),
                evidence=s.get("evidence", ""),
                confidence=float(s.get("confidence", 0.0)),
                source_type=s.get("source_type", "document"),
                source_id=s.get("source_id"),
                source_name=s.get("source_name"),
                source_uri=s.get("source_uri"),
                status=s.get("status") or s.get("validation_status", "PASS"),
                review_status=s.get("review_status", "ai_extracted")
            ))

        validations = []
        for v in data.get("validation", []):
            validations.append(ValidationResult(
                rule=v.get("rule") or v.get("rule_name", "Rule"),
                status=v.get("status", "PASS"),
                severity=v.get("severity", "INFO"),
                message=v.get("message", ""),
                field=v.get("field") or v.get("field_name", "")
            ))

        enrich_raw = data.get("enrichment", {})
        enrichment = AIEnrichment(
            search_terms=enrich_raw.get("search_terms", []),
            category_path=enrich_raw.get("category_path", []),
            suggested_applications=enrich_raw.get("suggested_applications", []),
            search_summary=enrich_raw.get("search_summary", "")
        )

        score_raw = data.get("quality_score", {})
        q_score = ProductQualityScore(
            overall_score=score_raw.get("overall_score", 0),
            completeness=score_raw.get("completeness", 0),
            extraction_quality=score_raw.get("extraction_quality", 0),
            validation_quality=score_raw.get("validation_quality", 0),
            evidence_coverage=score_raw.get("evidence_coverage", 0),
            consistency=score_raw.get("consistency", 0),
            status_category=score_raw.get("status_category", "REQUIRES MANUAL REVIEW")
        )

        return ProductIntelligenceRecord(
            product_id=data.get("product_id", "LEGACY-001"),
            product=prod_info,
            specifications=specs,
            validation=validations,
            enrichment=enrichment,
            quality_score=q_score,
            review_status=data.get("review_status", "ai_extracted"),
            raw_sources=data.get("raw_sources", [])
        )
    except Exception as e:
        logger.error(f"Failed to parse legacy JSON record: {e}")
        return None


def migrate_legacy_uploads(uploads_dir: str = "uploads") -> Dict[str, Any]:
    """Scans uploads/ directory and migrates legacy JSON records to the database."""
    init_db()
    if not os.path.exists(uploads_dir):
        return {"migrated": 0, "errors": 0, "status": "no uploads directory"}

    migrated_count = 0
    error_count = 0

    with get_db_context() as db:
        repo = ProductRepository(db)
        for fname in os.listdir(uploads_dir):
            if fname.endswith(".json") and not fname.startswith("CATALOG-"):
                fpath = os.path.join(uploads_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict) and "product_id" in data and "product" in data:
                        # Check if product already in db
                        existing = repo.get_by_product_id(data["product_id"])
                        if not existing:
                            rec = dict_to_record(data)
                            if rec:
                                repo.save_full_record(rec, change_summary="Imported from legacy JSON file")
                                migrated_count += 1
                except Exception as e:
                    logger.error(f"Error migrating {fpath}: {e}")
                    error_count += 1

    return {
        "migrated": migrated_count,
        "errors": error_count,
        "status": "completed"
    }
