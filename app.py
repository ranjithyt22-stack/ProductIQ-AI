"""
ProductIQ AI - Main Gradio Web Application
AI-Powered Product Intelligence for Industrial Commerce & Scalable Catalog Processing
"""

import os
import json
import csv
import io
import time
import shutil
import pandas as pd
import pymupdf as fitz
import gradio as gr

from backend.utils import generate_sample_pneumatic_cylinder_pdf, export_record_json, export_record_csv
from backend.pipeline import process_product_intelligence
from backend.models import ProductIntelligenceRecord, CatalogResult, CatalogProcessingStatus
from backend.catalog import parse_catalog_csv, process_catalog_batch, export_catalog_csv, export_catalog_json
from backend.ingestion import IngestionError, ingest_sources, save_upload

SAMPLE_PDF_PATH = os.path.join("data", "ProductIQ_Test_Industrial_Pneumatic_Cylinder.pdf")
SAMPLE_CATALOG_CSV = os.path.join("data", "sample_catalog.csv")
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)


def load_sample_datasheet():
    """Generates and loads the sample industrial pneumatic cylinder PDF."""
    pdf_path = generate_sample_pneumatic_cylinder_pdf(SAMPLE_PDF_PATH)
    sample_dest = os.path.join(UPLOADS_DIR, "sample_pneumatic_cylinder.pdf")
    shutil.copy2(pdf_path, sample_dest)
    return (
        pdf_path,     # pdf_input (display path)
        sample_dest,  # pdf_state (persistent stored path)
        "Acme Industrial Systems Pvt. Ltd.",
        "Pneumatic Cylinder PC-50-100",
        "PC-50-100",
        "Heavy-duty double acting pneumatic cylinder designed for precise industrial automation.",
        "https://acmeindustrial.com/products/pc-50-100"
    )


def load_sample_catalog():
    """Returns sample catalog CSV filepath."""
    if not os.path.exists(SAMPLE_CATALOG_CSV):
        # Fallback inline creation if missing
        with open(SAMPLE_CATALOG_CSV, "w", encoding="utf-8") as f:
            f.write("product_name,manufacturer,product_code,description,product_url,source_file\n")
            f.write("Pneumatic Cylinder PC-50-100,Acme Industrial Systems Pvt. Ltd.,PC-50-100,Heavy-duty double acting pneumatic cylinder.,,ProductIQ_Test_Industrial_Pneumatic_Cylinder.pdf\n")
            f.write("High-Flow Solenoid Pressure Valve,FlowControl Tech Inc,PV-200,2-way solenoid operated directional control pressure valve.,,\n")
    return SAMPLE_CATALOG_CSV


def format_quality_badge(quality_dict: dict) -> str:
    """Renders sleek HTML score badge and breakdown cards."""
    score = quality_dict.get("overall_score", 0)
    category = quality_dict.get("status_category", "REQUIRES MANUAL REVIEW")

    if category == "READY FOR COMMERCE":
        color = "#10B981"  # Green
        bg_color = "#ECFDF5"
    elif category == "REVIEW RECOMMENDED":
        color = "#F59E0B"  # Yellow/Orange
        bg_color = "#FFFBEB"
    else:
        color = "#EF4444"  # Red
        bg_color = "#FEF2F2"

    html = f"""
    <div style="background-color: {bg_color}; border: 2px solid {color}; border-radius: 12px; padding: 20px; margin-bottom: 20px; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 14px; font-weight: 600; text-transform: uppercase; color: #4B5563; letter-spacing: 1px;">Product Quality Readiness</span>
                <h2 style="margin: 4px 0 0 0; color: {color}; font-size: 26px; font-weight: 800;">{category}</h2>
            </div>
            <div style="text-align: right; background: white; padding: 10px 24px; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <span style="font-size: 12px; font-weight: 600; color: #6B7280; text-transform: uppercase;">Overall Score</span>
                <div style="font-size: 32px; font-weight: 900; color: {color};">{score} <span style="font-size: 16px; color: #9CA3AF;">/ 100</span></div>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid #E5E7EB; margin: 16px 0;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; text-align: center;">
            <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;">
                <div style="font-size: 11px; color: #6B7280; font-weight: 600;">COMPLETENESS</div>
                <div style="font-size: 18px; font-weight: 700; color: #1F2937;">{quality_dict.get('completeness', 0)}%</div>
            </div>
            <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;">
                <div style="font-size: 11px; color: #6B7280; font-weight: 600;">EXTRACTION</div>
                <div style="font-size: 18px; font-weight: 700; color: #1F2937;">{quality_dict.get('extraction_quality', 0)}%</div>
            </div>
            <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;">
                <div style="font-size: 11px; color: #6B7280; font-weight: 600;">VALIDATION</div>
                <div style="font-size: 18px; font-weight: 700; color: #1F2937;">{quality_dict.get('validation_quality', 0)}%</div>
            </div>
            <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;">
                <div style="font-size: 11px; color: #6B7280; font-weight: 600;">EVIDENCE</div>
                <div style="font-size: 18px; font-weight: 700; color: #1F2937;">{quality_dict.get('evidence_coverage', 0)}%</div>
            </div>
            <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;">
                <div style="font-size: 11px; color: #6B7280; font-weight: 600;">CONSISTENCY</div>
                <div style="font-size: 18px; font-weight: 700; color: #1F2937;">{quality_dict.get('consistency', 0)}%</div>
            </div>
        </div>
    </div>
    """
    return html


def format_catalog_summary_cards(catalog_dict: dict) -> str:
    """Renders catalog summary cards & aggregate quality stats."""
    total = catalog_dict.get("total_products", 0)
    processed = catalog_dict.get("processed_products", 0)
    failed = catalog_dict.get("failed_products", 0)
    ready = catalog_dict.get("ready_products", 0)
    needs_review = catalog_dict.get("review_required_products", 0)

    avg_score = catalog_dict.get("average_quality_score", 0.0)
    avg_ev = catalog_dict.get("average_evidence_coverage", 0.0)
    val_rate = catalog_dict.get("validation_pass_rate", 0.0)

    html = f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px; font-family: sans-serif;">
        <h3 style="margin: 0 0 16px 0; color: #0F172A; font-size: 20px;">Catalog Processing Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; text-align: center;">
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">TOTAL PRODUCTS</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{total}</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">PROCESSED</div>
                <div style="font-size: 24px; font-weight: 800; color: #2563EB;">{processed}</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">READY FOR COMMERCE</div>
                <div style="font-size: 24px; font-weight: 800; color: #10B981;">{ready}</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">NEEDS REVIEW</div>
                <div style="font-size: 24px; font-weight: 800; color: #F59E0B;">{needs_review}</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">FAILED</div>
                <div style="font-size: 24px; font-weight: 800; color: #EF4444;">{failed}</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">AVG QUALITY SCORE</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{avg_score} <span style="font-size: 12px; color: #94A3B8;">/100</span></div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">EVIDENCE COVERAGE</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{avg_ev}%</div>
            </div>
            <div style="background: white; padding: 14px; border-radius: 10px; border: 1px solid #CBD5E1;">
                <div style="font-size: 11px; color: #64748B; font-weight: 700;">VALIDATION PASS RATE</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{val_rate}%</div>
            </div>
        </div>
    </div>
    """
    return html


def format_catalog_dataframe(catalog_products: list) -> pd.DataFrame:
    """Converts catalog products list into clean DataFrame."""
    rows = []
    for p in catalog_products:
        rows.append({
            "Product ID": p.get("product_id", ""),
            "Product Name": p.get("product_name", ""),
            "Manufacturer": p.get("manufacturer", "") or "—",
            "Product Code": p.get("product_code", "") or "—",
            "Category": p.get("category", "") or "Industrial Equipment",
            "Quality Score": f"{p.get('quality_score', 0)} / 100",
            "Readiness": p.get("readiness_status", "REQUIRES MANUAL REVIEW"),
            "Evidence %": f"{p.get('evidence_coverage', 0)}%",
            "Status": p.get("status", "QUEUED"),
            "Error Details": p.get("error_message") or "None"
        })
    if not rows:
        return pd.DataFrame(columns=["Product ID", "Product Name", "Manufacturer", "Product Code", "Category", "Quality Score", "Readiness", "Evidence %", "Status", "Error Details"])
    return pd.DataFrame(rows)


def format_overview_md(prod_info: dict, enrichment_dict: dict) -> str:
    """Formats markdown view for Product Overview and AI Enrichment."""
    name = prod_info.get("product_name") or "N/A"
    mfr = prod_info.get("manufacturer") or "N/A"
    code = prod_info.get("product_code") or "N/A"
    cat = prod_info.get("category") or "N/A"
    desc = prod_info.get("description") or "No description available."

    cat_path = " → ".join(enrichment_dict.get("category_path", ["Industrial Equipment"]))
    search_terms = ", ".join([f"`{t}`" for t in enrichment_dict.get("search_terms", [])])
    apps = "\n".join([f"- {a}" for a in enrichment_dict.get("suggested_applications", [])])
    summary = enrichment_dict.get("search_summary", "")

    md = f"""
### Product Header Information
- **Product Name:** {name}
- **Manufacturer:** {mfr}
- **Product/Part Code:** `{code}`
- **Category:** {cat}

**Description:**
> {desc}

---

### AI-Generated Metadata & Taxonomy
*(Clearly labeled: AI-Generated Enrichment based strictly on source facts)*

**Taxonomy Category Path:**
`{cat_path}`

**Search Terms & Keywords:**
{search_terms if search_terms else "None"}

**Suggested Industrial Applications:**
{apps if apps else "- Standard Industrial Operations"}

**Search Summary:**
> {summary}
"""
    return md


def format_specs_dataframe(specs_list: list) -> pd.DataFrame:
    """Converts specification items into clean pandas DataFrame."""
    rows = []
    for s in specs_list:
        rows.append({
            "Attribute": s.get("name", ""),
            "Value": s.get("value", ""),
            "Unit": s.get("unit") or "—",
            "Confidence": f"{s.get('confidence', 0)}%",
            "Source Page": f"Page {s.get('page')}" if s.get('page') else "Document",
            "Validation Status": s.get("status", "PASS"),
            "Review Status": s.get("review_status", "ai_extracted").replace("_", " ").title()
        })
    if not rows:
        return pd.DataFrame(columns=["Attribute", "Value", "Unit", "Confidence", "Source Page", "Validation Status", "Review Status"])
    return pd.DataFrame(rows)


def format_validation_md(validation_list: list) -> str:
    """Renders validation results markdown with status badges."""
    if not validation_list:
        return "No validation issues recorded."

    md_lines = ["### Validation & Consistency Results\n"]
    for v in validation_list:
        status = v.get("status", "PASS")
        icon = "[PASS]" if status == "PASS" else ("Wait" if status == "WARNING" else "[FAIL]")
        rule = v.get("rule", "Validation Rule")
        msg = v.get("message", "")
        field = v.get("field", "")

        md_lines.append(f"- {icon} **[{status}]** `{rule}` ({field}): {msg}")

    return "\n".join(md_lines)


def format_evidence_card(attr_name: str, record_dict: dict) -> str:
    """Formats evidence traceability details for a selected specification attribute."""
    if not attr_name or not record_dict:
        return "Select an attribute to inspect evidence details."

    specs = record_dict.get("specifications", [])
    target = next((s for s in specs if s.get("name") == attr_name), None)
    if not target:
        return f"No specification found matching '{attr_name}'."

    val = target.get("value", "")
    unit = target.get("unit") or ""
    conf = target.get("confidence", 0)
    page = target.get("page") or 1
    evidence_text = target.get("evidence") or "Evidence text could not be precisely isolated."

    sources = record_dict.get("raw_sources", [])
    source_file = sources[0].get("filename", "Document") if sources else "Uploaded Document"

    # Construct clean user-facing value string in Python
    extracted_val_str = f"{val} {unit}".strip() if unit else str(val).strip()

    card_md = f"""
### Evidence & Source Traceability

- **Attribute Name:** `{attr_name}`
- **Extracted Value:** `{extracted_val_str}`
- **Confidence Score:** **{conf}%**
- **Source File:** `{source_file}`
- **Source Page Number:** **Page {page}**

#### Verbatim Document Evidence Quote:
> "{evidence_text}"

*Note: ProductIQ AI isolates verbatim sentence snippets from the original source PDF to prevent model hallucinations.*
"""
    return card_md


def clear_pdf_ui_handler():
    """Clear callback for when the user clicks 'X' / clear on the file component."""
    return None, ""


# Alias for test suite compatibility
handle_pdf_clear = clear_pdf_ui_handler


def handle_pdf_upload(pdf_file):
    """
    Upload handler that validates uploaded file(s), copies them into persistent uploads/ storage,
    and returns persistent path(s) to pdf_state and status HTML to status_output.
    DOES NOT run LLM inference.
    DOES NOT re-render other components (prevents loading spinners and flickering).
    """
    if not pdf_file:
        return handle_pdf_clear()

    items = pdf_file if isinstance(pdf_file, list) else [pdf_file]
    paths = []
    names = []

    for item in items:
        src_path = item if isinstance(item, str) else (getattr(item, "name", None) or str(item))
        if not src_path or not os.path.exists(src_path):
            err_html = """
            <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px; font-family: sans-serif;">
                <h4 style="margin: 0 0 8px 0;">Upload Error</h4>
                <p style="margin: 0;">Uploaded file does not exist on disk. Please select a valid document.</p>
            </div>
            """
            return None, err_html

        try:
            dest_path = save_upload(src_path)
            paths.append(dest_path)
            names.append(os.path.basename(src_path))
        except IngestionError as error:
            err_html = f"""
            <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px; font-family: sans-serif;">
                <h4 style="margin: 0 0 8px 0;">Upload Error</h4>
                <p style="margin: 0;">{error}</p>
            </div>
            """
            return None, err_html

    if not paths:
        return handle_pdf_clear()

    state_path = paths[0] if len(paths) == 1 else paths
    file_list_str = ", ".join(names)

    info_html = f"""
    <div style="background-color: #EFF6FF; border: 1px solid #3B82F6; color: #1E40AF; padding: 16px; border-radius: 8px; font-family: sans-serif;">
        <h4 style="margin: 0 0 4px 0;">Source File(s) Loaded: {file_list_str}</h4>
        <p style="margin: 0;">Stored securely. Click <b>Analyze Single Product with AI</b> to execute extraction.</p>
    </div>
    """

    return state_path, info_html


def handle_multi_source_upload(files):
    """Persist every selected source; this callback never runs extraction or an LLM."""
    paths = []
    try:
        for item in files or []:
            source = item if isinstance(item, str) else getattr(item, "name", None)
            if source:
                paths.append(save_upload(source))
    except IngestionError as error:
        return [], f"<div class='error'>Upload Error: {error}</div>"
    names = ", ".join(os.path.basename(p).split("_", 1)[-1] for p in paths)
    return paths, (f"<div>Sources stored: {names}. Click Analyze to process them.</div>" if paths else "")


def analyze_multi_source_ui(file_paths, urls_text, supplementary_text, manufacturer, product_name, product_code):
    """Explicit-only multi-source analysis entry point."""
    urls = [line.strip() for line in (urls_text or "").splitlines() if line.strip()]
    try:
        documents = ingest_sources(file_paths or [], urls, supplementary_text)
    except IngestionError as error:
        return _analysis_error(f"Input Error: {error}")
    record, error = process_product_intelligence(
        manufacturer=manufacturer, product_name=product_name, product_code=product_code,
        description=None, source_documents=documents
    )
    if error or not record:
        return _analysis_error(f"Analysis Failed: {error or 'No structured record was produced.'}")
    return _format_analysis_record(record)


def _analysis_error(message):
    update = gr.update(choices=[], value=None)
    return (f"<div class='error'>{message}</div>", "", pd.DataFrame(), "", update,
            "Select an attribute to view evidence.", update, "", None, None, {})


def _format_analysis_record(record):
    record_dict = record.to_dict()
    spec_names = [s.get("name") for s in record_dict.get("specifications", [])]
    first_attr = spec_names[0] if spec_names else None
    json_filename = os.path.join(UPLOADS_DIR, f"{record.product_id}.json")
    csv_filename = os.path.join(UPLOADS_DIR, f"{record.product_id}.csv")
    with open(json_filename, "w", encoding="utf-8") as f: f.write(export_record_json(record))
    with open(csv_filename, "w", encoding="utf-8") as f: f.write(export_record_csv(record))
    update = gr.update(choices=spec_names, value=first_attr)
    return (format_quality_badge(record_dict.get("quality_score", {})),
            format_overview_md(record_dict.get("product", {}), record_dict.get("enrichment", {})),
            format_specs_dataframe(record_dict.get("specifications", [])),
            format_validation_md(record_dict.get("validation", [])), update,
            format_evidence_card(first_attr, record_dict), update,
            export_record_json(record), json_filename, csv_filename, record_dict)


def analyze_product_ui(pdf_state_path, manufacturer, product_name, product_code, description, product_url):
    """Main callback handler for single product and multi-source analysis."""
    # 1. Gather all active sources
    files_to_ingest = []
    if pdf_state_path:
        if isinstance(pdf_state_path, list):
            files_to_ingest = [f for f in pdf_state_path if isinstance(f, str) and os.path.exists(f)]
        elif isinstance(pdf_state_path, str) and os.path.exists(pdf_state_path):
            files_to_ingest = [pdf_state_path]

    urls_to_ingest = []
    if product_url and product_url.strip():
        raw_urls = re.split(r"[\n,]", product_url)
        urls_to_ingest = [u.strip() for u in raw_urls if u.strip()]

    pasted_text = description.strip() if description and description.strip() else None

    # Input Validation
    if not files_to_ingest and not urls_to_ingest and not pasted_text:
        error_html = """
        <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px; font-family: sans-serif;">
            <h4 style="margin: 0 0 8px 0;">Input Required</h4>
            <p style="margin: 0;">Please upload product document file(s), enter a product webpage URL, or enter a text description.</p>
        </div>
        """
        return (
            error_html, "", pd.DataFrame(), "", gr.Dropdown(choices=[]), "Select attribute to view evidence.",
            gr.Dropdown(choices=[]), "", None, None, {}
        )


    try:
        source_docs = ingest_sources(files=files_to_ingest, urls=urls_to_ingest, text=pasted_text)
    except IngestionError as err:
        error_html = f"""
        <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px; font-family: sans-serif;">
            <h4 style="margin: 0 0 8px 0;">Ingestion Error</h4>
            <p style="margin: 0;">{err}</p>
        </div>
        """
        return (
            error_html, "", pd.DataFrame(), "", gr.Dropdown(choices=[]), "Select attribute to view evidence.",
            gr.Dropdown(choices=[]), "", None, None, {}
        )

    record, err = process_product_intelligence(
        manufacturer=manufacturer or None,
        product_name=product_name or None,
        product_code=product_code or None,
        source_documents=source_docs
    )

    if err or not record:
        error_html = f"""
        <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px; font-family: sans-serif;">
            <h4 style="margin: 0 0 8px 0;">Analysis Failed</h4>
            <p style="margin: 0;">{err or 'Failed to extract structured product record.'}</p>
        </div>
        """
        return (
            error_html, "", pd.DataFrame(), "", gr.Dropdown(choices=[]), "Select attribute to view evidence.",
            gr.Dropdown(choices=[]), "", None, None, {}
        )

    return _format_analysis_record(record)




def update_evidence_ui(attr_name, record_dict):
    return format_evidence_card(attr_name, record_dict)


def apply_human_override_ui(attr_name, new_val, new_unit, record_dict):
    """Callback for applying human review overrides."""
    if not record_dict or not attr_name:
        return "Please run an analysis first.", pd.DataFrame(), "", None, None, record_dict

    specs = record_dict.get("specifications", [])
    updated = False
    for s in specs:
        if s.get("name") == attr_name:
            s["value"] = new_val
            if new_unit:
                s["unit"] = new_unit
            s["review_status"] = "human_verified"
            s["confidence"] = 100
            updated = True
            break

    if updated:
        record_dict["review_status"] = "human_verified"
        specs_df = format_specs_dataframe(specs)

        p_id = record_dict.get("product_id", "record")
        json_filename = os.path.join(UPLOADS_DIR, f"{p_id}.json")
        csv_filename = os.path.join(UPLOADS_DIR, f"{p_id}.csv")

        json_str = json.dumps(record_dict, indent=2, ensure_ascii=False)
        with open(json_filename, "w", encoding="utf-8") as f:
            f.write(json_str)

        output_csv = io.StringIO()
        writer = csv.writer(output_csv)
        writer.writerow(["product_name", "manufacturer", "product_code", "category", "attribute", "value", "unit", "confidence", "source", "page", "validation_status", "review_status"])
        p_info = record_dict.get("product", {})
        for s in specs:
            writer.writerow([
                p_info.get("product_name", ""), p_info.get("manufacturer", ""), p_info.get("product_code", ""), p_info.get("category", ""),
                s.get("name", ""), s.get("value", ""), s.get("unit", ""), f"{s.get('confidence', 0)}%", "Document", s.get("page", 1), s.get("status", "PASS"), s.get("review_status", "human_verified")
            ])
        csv_str = output_csv.getvalue()
        with open(csv_filename, "w", encoding="utf-8") as f:
            f.write(csv_str)

        msg = f"Attribute '{attr_name}' updated to '{new_val} {new_unit or ''}'. Marked as HUMAN VERIFIED."
        return msg, specs_df, json_str, json_filename, csv_filename, record_dict

    return "Attribute not found.", pd.DataFrame(), "", None, None, record_dict


# ==============================================================================
# CATALOG ENGINE GRADIO HANDLERS
# ==============================================================================

def analyze_catalog_ui(csv_file, pdf_files):
    """Main callback for catalog batch processing."""
    if not csv_file and not pdf_files:
        error_html = """
        <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px;">
            <h4>No Catalog Source Provided</h4>
            <p>Please upload a Catalog CSV file or one/more Product PDF datasheets.</p>
        </div>
        """
        return error_html, pd.DataFrame(), gr.Dropdown(choices=[]), "", "", None, None, {}

    # Map uploaded PDFs
    pdf_files_map = {}
    if pdf_files:
        for f in pdf_files:
            filename = os.path.basename(f.name)
            pdf_files_map[filename] = f.name

    # Parse items
    input_items = []
    if csv_file:
        input_items = parse_catalog_csv(csv_file)

    if not input_items and pdf_files_map:
        # Construct catalog items directly from PDF files
        for idx, (filename, fullpath) in enumerate(pdf_files_map.items(), start=1):
            clean_title = os.path.splitext(filename)[0].replace("_", " ").title()
            input_items.append({
                "product_id": f"PIQ-{idx:06d}",
                "product_name": clean_title,
                "source_file": filename,
                "source_id": f"pdf_file_{idx:03d}"
            })

    if not input_items:
        error_html = """
        <div style="background-color: #FEF2F2; border: 1px solid #EF4444; color: #991B1B; padding: 16px; border-radius: 8px;">
            <h4>Empty Catalog</h4>
            <p>Could not parse valid catalog rows from the uploaded CSV.</p>
        </div>
        """
        return error_html, pd.DataFrame(), gr.Dropdown(choices=[]), "", "", None, None, {}

    # Execute batch processing
    cat_result = process_catalog_batch(input_items, pdf_files_map=pdf_files_map)
    cat_dict = cat_result.to_dict()

    summary_html = format_catalog_summary_cards(cat_dict)
    catalog_df = format_catalog_dataframe(cat_dict.get("products", []))

    # Product IDs for inspector dropdown
    prod_choices = [f"{p['product_id']} - {p['product_name']}" for p in cat_dict.get("products", [])]
    first_choice = prod_choices[0] if prod_choices else None

    # Exports
    json_str = export_catalog_json(cat_result)
    csv_str = export_catalog_csv(cat_result)

    cat_json_path = os.path.join(UPLOADS_DIR, f"{cat_result.catalog_id}.json")
    cat_csv_path = os.path.join(UPLOADS_DIR, f"{cat_result.catalog_id}.csv")

    with open(cat_json_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    with open(cat_csv_path, "w", encoding="utf-8") as f:
        f.write(csv_str)

    dropdown_update = gr.Dropdown(choices=prod_choices, value=first_choice)

    return (
        summary_html,
        catalog_df,
        dropdown_update,
        json_str,
        csv_str,
        cat_json_path,
        cat_csv_path,
        cat_dict
    )


def filter_catalog_table_ui(search_query, readiness_filter, status_filter, cat_dict):
    """Filters catalog table dynamically."""
    if not cat_dict or "products" not in cat_dict:
        return pd.DataFrame()

    prods = cat_dict.get("products", [])
    filtered = []

    sq = (search_query or "").strip().lower()

    for p in prods:
        # Search query matching
        pid = str(p.get("product_id", "")).lower()
        pname = str(p.get("product_name", "")).lower()
        pcode = str(p.get("product_code", "")).lower()

        if sq and (sq not in pid and sq not in pname and sq not in pcode):
            continue

        # Readiness filter
        readiness = p.get("readiness_status", "")
        if readiness_filter and readiness_filter != "All" and readiness != readiness_filter:
            continue

        # Status filter
        status = p.get("status", "")
        if status_filter and status_filter != "All" and status != status_filter:
            continue

        filtered.append(p)

    return format_catalog_dataframe(filtered)


def inspect_catalog_product_ui(selected_choice, cat_dict):
    """Inspects detailed single product record selected from catalog."""
    if not selected_choice or not cat_dict or "products" not in cat_dict:
        return "Select a product to inspect detail.", pd.DataFrame(), "", ""

    target_pid = selected_choice.split(" - ")[0].strip()
    prods = cat_dict.get("products", [])
    target = next((p for p in prods if p.get("product_id") == target_pid), None)

    if not target or not target.get("record"):
        return f"No detailed record available for {target_pid} (Status: {target.get('status', 'N/A') if target else 'N/A'}).", pd.DataFrame(), "", ""

    record_dict = target.get("record", {})
    overview_md = format_overview_md(record_dict.get("product", {}), record_dict.get("enrichment", {}))
    specs_df = format_specs_dataframe(record_dict.get("specifications", []))
    val_md = format_validation_md(record_dict.get("validation", []))
    json_preview = json.dumps(record_dict, indent=2, ensure_ascii=False)

    return overview_md, specs_df, val_md, json_preview


# ==============================================================================
# GRADIO INTERFACE LAYOUT
# ==============================================================================

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate"
)

with gr.Blocks() as demo:

    pdf_state = gr.State(value=None)
    record_state = gr.State({})
    catalog_state = gr.State({})

    # 1. Header
    gr.Markdown(
        "# ProductIQ AI\n"
        "### AI-Powered Product Intelligence for Industrial Commerce & Catalog Engine\n"
        "*Convert unstructured datasheets & catalogs into validated, evidence-backed, commerce-ready product data.*"
    )

    with gr.Tabs():

        # ======================================================================
        # TAB 1: SINGLE PRODUCT ANALYZER
        # ======================================================================
        with gr.TabItem("Single Product Analyzer"):
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="Upload Product Files / Datasheets (PDF, DOCX, CSV, XLSX, TXT, MD, Images)",
                        file_types=[".pdf", ".docx", ".csv", ".xlsx", ".xls", ".txt", ".md", ".png", ".jpg", ".jpeg"],
                        file_count="multiple",
                        type="filepath",
                        value=None
                    )
                    sample_btn = gr.Button("Load Sample Pneumatic Cylinder Datasheet", variant="secondary")

                with gr.Column(scale=2):
                    with gr.Row():
                        mfr_input = gr.Textbox(label="Manufacturer (Optional)", placeholder="Enter manufacturer name (e.g. Acme Corp)")
                        pname_input = gr.Textbox(label="Product Name (Optional)", placeholder="Enter product title or model name")
                    with gr.Row():
                        pcode_input = gr.Textbox(label="Part Number / Code (Optional)", placeholder="Enter part / SKU code")
                        purl_input = gr.Textbox(label="Product Webpage URL (Optional)", placeholder="https://example.com/products/model-100")
                    desc_input = gr.Textbox(
                        label="Product Description / Supplementary Text (Optional)",
                        placeholder="Enter technical specifications, paste supplementary text, or list additional notes...",
                        lines=3
                    )

            analyze_btn = gr.Button("Analyze Single Product with AI", variant="primary", size="lg")

            status_output = gr.HTML()

            with gr.Tabs():
                with gr.TabItem("Product Overview & AI Enrichment"):
                    overview_md_output = gr.Markdown("Run product analysis to view overview and taxonomy enrichment.")

                with gr.TabItem("Technical Specifications"):
                    specs_table_output = gr.DataFrame(interactive=False)

                with gr.TabItem("Validation & Consistency"):
                    validation_md_output = gr.Markdown("Run product analysis to view validation results.")

                with gr.TabItem("Evidence & Traceability"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            evidence_attr_dropdown = gr.Dropdown(label="Select Attribute to Inspect Evidence", choices=[])
                        with gr.Column(scale=2):
                            evidence_card_output = gr.Markdown("Select an attribute to inspect verbatim evidence quotes.")

                with gr.TabItem("Human Review & Verification"):
                    gr.Markdown("### Override or Confirm Product Specifications")
                    with gr.Row():
                        review_attr_dropdown = gr.Dropdown(label="Attribute to Edit", choices=[])
                        review_val_input = gr.Textbox(label="Corrected Value", placeholder="e.g. 2.0")
                        review_unit_input = gr.Textbox(label="Corrected Unit", placeholder="e.g. kg")
                    apply_review_btn = gr.Button("Confirm & Mark Human Verified", variant="primary")
                    review_status_msg = gr.Markdown()

                with gr.TabItem("Export & Raw Data"):
                    with gr.Row():
                        json_download_btn = gr.File(label="Download Full Intelligence JSON")
                        csv_download_btn = gr.File(label="Download Attribute CSV")
                    raw_json_output = gr.Code(label="Raw JSON Output", language="json", lines=20)

        # ======================================================================
        # TAB 2: SCALABLE CATALOG ENGINE
        # ======================================================================
        with gr.TabItem("Catalog Engine"):
            gr.Markdown("### Scalable Industrial Product Catalog Engine")
            gr.Markdown("Ingest CSV catalogs or multiple PDF datasheets to generate validated, enriched, commerce-ready product catalogs.")

            with gr.Row():
                with gr.Column(scale=1):
                    csv_catalog_input = gr.File(label="Upload Catalog CSV", file_types=[".csv"])
                    sample_catalog_btn = gr.Button("Load Sample Industrial Catalog (5 Products)", variant="secondary")
                with gr.Column(scale=1):
                    pdf_catalog_input = gr.File(label="Upload Multiple Product PDFs (Optional)", file_count="multiple", file_types=[".pdf"])

            analyze_catalog_btn = gr.Button("Analyze Catalog Batch", variant="primary", size="lg")

            catalog_summary_output = gr.HTML()

            with gr.Row():
                cat_search_input = gr.Textbox(label="Search Product Name / Code / ID", placeholder="Type keywords...")
                cat_readiness_filter = gr.Dropdown(label="Filter Readiness", choices=["All", "READY FOR COMMERCE", "REVIEW RECOMMENDED", "REQUIRES MANUAL REVIEW", "FAILED"], value="All")
                cat_status_filter = gr.Dropdown(label="Filter Status", choices=["All", "COMPLETED", "FAILED", "REVIEW_REQUIRED"], value="All")

            catalog_table_output = gr.DataFrame(interactive=False)

            with gr.Accordion("Inspect Detailed Product Intelligence from Catalog", open=True):
                cat_inspect_dropdown = gr.Dropdown(label="Select Catalog Product to Inspect", choices=[])
                with gr.Tabs():
                    with gr.TabItem("Overview & Enrichment"):
                        cat_inspect_overview = gr.Markdown("Select a product above to inspect details.")
                    with gr.TabItem("Specifications"):
                        cat_inspect_specs = gr.DataFrame(interactive=False)
                    with gr.TabItem("Validation"):
                        cat_inspect_validation = gr.Markdown()
                    with gr.TabItem("JSON Record"):
                        cat_inspect_json = gr.Code(language="json", lines=15)

            with gr.Row():
                cat_json_download = gr.File(label="Download Catalog JSON (Full Nested Intelligence)")
                cat_csv_download = gr.File(label="Download Catalog CSV (Commerce Summary)")

            cat_json_raw = gr.Code(label="Raw Catalog JSON Output", language="json", lines=15, visible=False)
            cat_csv_raw = gr.Code(label="Raw Catalog CSV Output", language=None, lines=15, visible=False)

    # ======================================================================
    # SINGLE PRODUCT EVENT BINDINGS
    # ======================================================================
    # Handle upload and clear events on pdf_input component cleanly without multi-component re-renders
    pdf_input.upload(
        fn=handle_pdf_upload,
        inputs=[pdf_input],
        outputs=[pdf_state, status_output]
    )

    pdf_input.clear(
        fn=handle_pdf_clear,
        inputs=[],
        outputs=[pdf_state, status_output]
    )

    sample_btn.click(
        fn=load_sample_datasheet,
        inputs=[],
        outputs=[pdf_input, pdf_state, mfr_input, pname_input, pcode_input, desc_input, purl_input]
    )

    analyze_btn.click(
        fn=analyze_product_ui,
        inputs=[pdf_state, mfr_input, pname_input, pcode_input, desc_input, purl_input],
        outputs=[
            status_output,
            overview_md_output,
            specs_table_output,
            validation_md_output,
            evidence_attr_dropdown,
            evidence_card_output,
            review_attr_dropdown,
            raw_json_output,
            json_download_btn,
            csv_download_btn,
            record_state
        ]
    )

    evidence_attr_dropdown.change(
        fn=update_evidence_ui,
        inputs=[evidence_attr_dropdown, record_state],
        outputs=[evidence_card_output]
    )

    apply_review_btn.click(
        fn=apply_human_override_ui,
        inputs=[review_attr_dropdown, review_val_input, review_unit_input, record_state],
        outputs=[
            review_status_msg,
            specs_table_output,
            raw_json_output,
            json_download_btn,
            csv_download_btn,
            record_state
        ]
    )

    # ======================================================================
    # CATALOG ENGINE EVENT BINDINGS
    # ======================================================================
    sample_catalog_btn.click(
        fn=load_sample_catalog,
        inputs=[],
        outputs=[csv_catalog_input]
    )

    analyze_catalog_btn.click(
        fn=analyze_catalog_ui,
        inputs=[csv_catalog_input, pdf_catalog_input],
        outputs=[
            catalog_summary_output,
            catalog_table_output,
            cat_inspect_dropdown,
            cat_json_raw,
            cat_csv_raw,
            cat_json_download,
            cat_csv_download,
            catalog_state
        ]
    )

    cat_search_input.change(
        fn=filter_catalog_table_ui,
        inputs=[cat_search_input, cat_readiness_filter, cat_status_filter, catalog_state],
        outputs=[catalog_table_output]
    )

    cat_readiness_filter.change(
        fn=filter_catalog_table_ui,
        inputs=[cat_search_input, cat_readiness_filter, cat_status_filter, catalog_state],
        outputs=[catalog_table_output]
    )

    cat_status_filter.change(
        fn=filter_catalog_table_ui,
        inputs=[cat_search_input, cat_readiness_filter, cat_status_filter, catalog_state],
        outputs=[catalog_table_output]
    )

    cat_inspect_dropdown.change(
        fn=inspect_catalog_product_ui,
        inputs=[cat_inspect_dropdown, catalog_state],
        outputs=[cat_inspect_overview, cat_inspect_specs, cat_inspect_validation, cat_inspect_json]
    )


if __name__ == "__main__":
    demo.launch(theme=theme, server_name="127.0.0.1", server_port=7860)
