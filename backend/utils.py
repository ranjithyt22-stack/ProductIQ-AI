"""
Utility module for ProductIQ AI.
Includes CSV/JSON export formatting, product record serialization, and demo PDF generator.
"""

import os
import json
import csv
import io
import pymupdf as fitz  # PyMuPDF
from typing import Dict, Any, Tuple
from backend.models import ProductIntelligenceRecord


def export_record_json(record: ProductIntelligenceRecord) -> str:
    """Serializes ProductIntelligenceRecord to formatted JSON string."""
    return json.dumps(record.to_dict(), indent=2, ensure_ascii=False)


def export_record_csv(record: ProductIntelligenceRecord) -> str:
    """Generates CSV string with one row per product attribute."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "product_name",
        "manufacturer",
        "product_code",
        "category",
        "attribute",
        "value",
        "unit",
        "confidence",
        "source",
        "page",
        "validation_status",
        "review_status"
    ])

    prod_dict = record.to_dict()
    prod_info = prod_dict.get("product", {})
    specs = prod_dict.get("specifications", [])

    p_name = prod_info.get("product_name") or ""
    mfr = prod_info.get("manufacturer") or ""
    code = prod_info.get("product_code") or ""
    cat = prod_info.get("category") or ""
    rev_status = prod_dict.get("review_status") or "ai_extracted"

    source_filename = "Document"
    if record.raw_sources:
        source_filename = record.raw_sources[0].get("filename", "Document")

    for s in specs:
        writer.writerow([
            p_name,
            mfr,
            code,
            cat,
            s.get("name", ""),
            s.get("value", ""),
            s.get("unit") or "",
            f"{s.get('confidence', 0)}%",
            source_filename,
            s.get("page") or 1,
            s.get("status", "PASS"),
            s.get("review_status", rev_status)
        ])

    return output.getvalue()


def generate_sample_pneumatic_cylinder_pdf(output_path: str) -> str:
    """
    Generates the test industrial pneumatic cylinder PDF datasheet using PyMuPDF.
    Path: data/ProductIQ_Test_Industrial_Pneumatic_Cylinder.pdf
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        return output_path

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    content = """ACME INDUSTRIAL SYSTEMS PVT. LTD.
TECHNICAL DATASHEET - INDUSTRIAL PNEUMATIC ACTUATOR

Product Name: Pneumatic Cylinder PC-50-100
Manufacturer: Acme Industrial Systems Pvt. Ltd.
Product Code: PC-50-100
Category: Pneumatic Cylinder
Description: Heavy-duty double acting pneumatic cylinder designed for precise industrial automation.

TECHNICAL SPECIFICATIONS:
- Bore Diameter: 50 mm
- Stroke Length: 100 mm
- Operating Pressure: 1 to 10 bar
- Operating Temperature: -10 to 60 °C
- Body Material: Aluminium Alloy
- Rod Material: Stainless Steel
- Piston Seal: Polyurethane
- Port Size: G1/4
- Action: Double Acting
- Mounting: Front Flange
- Weight: 1.8 kg
- Maximum Speed: 1.0 m/s

RECOMMENDED INDUSTRIAL APPLICATIONS:
1. Industrial automation
2. Assembly machines
3. Material handling
4. Packaging equipment
5. Manufacturing machinery

COMPLIANCE & CERTIFICATIONS: ISO 15552 Standard Compliant.
"""

    text_point = fitz.Point(40, 50)
    page.insert_text(text_point, content, fontsize=11)
    doc.save(output_path)
    doc.close()

    return output_path
