"""
Scalable Catalog Engine for ProductIQ AI.
Orchestrates CSV parsing, multi-PDF mapping, sequential fault-tolerant batch processing,
metrics aggregation, and catalog CSV/JSON exports.
"""

import os
import csv
import json
import io
import uuid
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

from backend.models import (
    CatalogProduct, CatalogResult, CatalogProcessingStatus,
    ProductIntelligenceRecord
)
from backend.pipeline import process_product_intelligence


def parse_catalog_csv(csv_source: Any) -> List[Dict[str, Any]]:
    """
    Parses catalog CSV file or string content into normalized item dicts.
    Handles missing optional columns gracefully.
    """
    items: List[Dict[str, Any]] = []

    if not csv_source:
        return items

    try:
        if isinstance(csv_source, str) and os.path.exists(csv_source):
            df = pd.read_csv(csv_source)
        elif hasattr(csv_source, "name") and os.path.exists(csv_source.name):
            df = pd.read_csv(csv_source.name)
        elif isinstance(csv_source, str):
            df = pd.read_csv(io.StringIO(csv_source))
        elif isinstance(csv_source, bytes):
            df = pd.read_csv(io.BytesIO(csv_source))
        else:
            return items
    except Exception:
        return items

    # Normalize column headers (lowercase, strip whitespace)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    for idx, row in df.iterrows():
        # Dynamic Product ID generation (e.g. PIQ-000001)
        product_id = f"PIQ-{idx+1:06d}"

        # Standardize column mappings
        pname = str(row.get("product_name") or row.get("name") or row.get("title") or "").strip()
        mfr = str(row.get("manufacturer") or row.get("brand") or row.get("vendor") or "").strip()
        pcode = str(row.get("product_code") or row.get("part_number") or row.get("sku") or "").strip()
        desc = str(row.get("description") or row.get("details") or "").strip()
        purl = str(row.get("product_url") or row.get("url") or "").strip()
        sfile = str(row.get("source_file") or row.get("pdf") or "").strip()

        # Handle 'nan' strings from pandas
        if pname.lower() == "nan": pname = ""
        if mfr.lower() == "nan": mfr = ""
        if pcode.lower() == "nan": pcode = ""
        if desc.lower() == "nan": desc = ""
        if purl.lower() == "nan": purl = ""
        if sfile.lower() == "nan": sfile = ""

        # Skip completely empty rows
        if not pname and not pcode and not desc and not sfile:
            continue

        items.append({
            "product_id": product_id,
            "product_name": pname or f"Catalog Item {idx+1}",
            "manufacturer": mfr,
            "product_code": pcode,
            "description": desc,
            "product_url": purl,
            "source_file": sfile,
            "source_id": f"csv_row_{idx+1:03d}"
        })

    return items


def aggregate_catalog_metrics(catalog_products: List[CatalogProduct], catalog_id: str = "") -> CatalogResult:
    """Computes overall catalog metrics, quality score averages, and pass rates."""
    if not catalog_id:
        catalog_id = f"CATALOG-{uuid.uuid4().hex[:6].upper()}"

    total = len(catalog_products)
    if total == 0:
        return CatalogResult(catalog_id=catalog_id, processing_status=CatalogProcessingStatus.COMPLETED)

    processed = sum(1 for p in catalog_products if p.status in [CatalogProcessingStatus.COMPLETED, "REVIEW_REQUIRED"])
    failed = sum(1 for p in catalog_products if p.status == CatalogProcessingStatus.FAILED)
    ready = sum(1 for p in catalog_products if p.readiness_status == "READY FOR COMMERCE" and p.status != CatalogProcessingStatus.FAILED)
    review_req = total - ready - failed

    successful_prods = [p for p in catalog_products if p.status != CatalogProcessingStatus.FAILED]

    if successful_prods:
        avg_q_score = round(sum(p.quality_score for p in successful_prods) / len(successful_prods), 1)
        avg_ev_cov = round(sum(p.evidence_coverage for p in successful_prods) / len(successful_prods), 1)
    else:
        avg_q_score = 0.0
        avg_ev_cov = 0.0

    # Validation Pass Rate & Conflict computation
    total_val_checks = 0
    passed_val_checks = 0
    prods_with_conf = 0
    open_c_count = 0
    resolved_c_count = 0
    crit_c_count = 0
    high_c_count = 0

    for p in catalog_products:
        if p.record:
            if p.record.validation:
                for v in p.record.validation:
                    total_val_checks += 1
                    if v.status == "PASS":
                        passed_val_checks += 1

            if p.record.conflicts:
                prods_with_conf += 1
                for c in p.record.conflicts:
                    if c.status == "OPEN":
                        open_c_count += 1
                        if c.severity == "CRITICAL":
                            crit_c_count += 1
                        elif c.severity == "HIGH":
                            high_c_count += 1
                    elif c.status == "RESOLVED":
                        resolved_c_count += 1

    val_pass_rate = round((passed_val_checks / total_val_checks * 100), 1) if total_val_checks > 0 else 100.0

    if failed == 0:
        overall_status = CatalogProcessingStatus.COMPLETED
    elif processed > 0:
        overall_status = CatalogProcessingStatus.PARTIAL
    else:
        overall_status = CatalogProcessingStatus.FAILED

    return CatalogResult(
        catalog_id=catalog_id,
        total_products=total,
        processed_products=processed,
        failed_products=failed,
        review_required_products=review_req,
        ready_products=ready,
        average_quality_score=avg_q_score,
        average_evidence_coverage=avg_ev_cov,
        validation_pass_rate=val_pass_rate,
        products_with_conflicts=prods_with_conf,
        open_conflicts=open_c_count,
        resolved_conflicts=resolved_c_count,
        critical_conflicts=crit_c_count,
        high_conflicts=high_c_count,
        products=catalog_products,
        processing_status=overall_status
    )



def process_catalog_batch(
    input_items: List[Dict[str, Any]],
    pdf_files_map: Optional[Dict[str, str]] = None,
    custom_pipeline_fn: Optional[Any] = None
) -> CatalogResult:
    """
    Executes sequential batch processing across all catalog items.
    Fault-tolerant: single product failure records an error and continues remaining items.
    """
    catalog_products: List[CatalogProduct] = []
    pipeline_fn = custom_pipeline_fn or process_product_intelligence

    for item in input_items:
        pid = item.get("product_id") or f"PIQ-{uuid.uuid4().hex[:6].upper()}"
        pname = item.get("product_name", "")
        mfr = item.get("manufacturer", "")
        pcode = item.get("product_code", "")
        desc = item.get("description", "")
        purl = item.get("product_url", "")
        sfile = item.get("source_file", "")

        # Locate PDF if mapped
        pdf_path = None
        if pdf_files_map and sfile and sfile in pdf_files_map:
            pdf_path = pdf_files_map[sfile]
        elif pdf_files_map and len(pdf_files_map) == 1 and not sfile:
            # If single PDF uploaded, map to item
            pdf_path = list(pdf_files_map.values())[0]

        cat_prod = CatalogProduct(
            product_id=pid,
            source_id=item.get("source_id", "input_001"),
            product_name=pname,
            manufacturer=mfr,
            product_code=pcode,
            status=CatalogProcessingStatus.PROCESSING
        )

        try:
            record, err = pipeline_fn(
                pdf_path=pdf_path,
                manufacturer=mfr,
                product_name=pname,
                product_code=pcode,
                description=desc,
                product_url=purl
            )

            if err or not record:
                cat_prod.status = CatalogProcessingStatus.FAILED
                cat_prod.error_message = err or "Unable to extract valid structured product data."
            else:
                record.product_id = pid  # Ensure record uses internal product_id
                rec_dict = record.to_dict()
                q_dict = rec_dict.get("quality_score", {})

                cat_prod.category = record.product.category or "Industrial Equipment"
                cat_prod.status = CatalogProcessingStatus.COMPLETED
                cat_prod.quality_score = q_dict.get("overall_score", 0)
                cat_prod.readiness_status = q_dict.get("status_category", "REQUIRES MANUAL REVIEW")
                cat_prod.evidence_coverage = q_dict.get("evidence_coverage", 0)
                cat_prod.confidence = float(q_dict.get("extraction_quality", 0))
                cat_prod.conflict_count = len(record.conflicts) if record.conflicts else 0
                cat_prod.critical_conflict_count = sum(1 for c in record.conflicts if c.severity == "CRITICAL" and c.status == "OPEN") if record.conflicts else 0
                cat_prod.record = record

        except Exception as e:
            cat_prod.status = CatalogProcessingStatus.FAILED
            cat_prod.error_message = f"Processing exception: {str(e)}"

        catalog_products.append(cat_prod)

    return aggregate_catalog_metrics(catalog_products)


def export_catalog_csv(catalog_result: CatalogResult) -> str:
    """Exports commerce-friendly tabular CSV summary for the entire catalog."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "product_id",
        "product_name",
        "manufacturer",
        "product_code",
        "category",
        "description",
        "quality_score",
        "readiness_status",
        "validation_status",
        "evidence_coverage",
        "processing_status",
        "error_message"
    ])

    for p in catalog_result.products:
        desc = p.record.product.description if p.record and p.record.product else ""
        writer.writerow([
            p.product_id,
            p.product_name,
            p.manufacturer,
            p.product_code,
            p.category,
            desc,
            p.quality_score,
            p.readiness_status,
            p.validation_status,
            f"{p.evidence_coverage}%",
            p.status,
            p.error_message
        ])

    return output.getvalue()


def export_catalog_json(catalog_result: CatalogResult) -> str:
    """Exports full nested catalog intelligence record in JSON format."""
    return json.dumps(catalog_result.to_dict(), indent=2, ensure_ascii=False)
