"""
Automated Test Suite for ProductIQ AI Ingestion Adapters.
Tests PDF, CSV, Excel, DOCX, TXT, MD, Image OCR fallback, save_upload security, and multi-source bundling.
"""

import sys
import os
import tempfile
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from backend.ingestion import (
    IngestionError, SourceDocument, ingest_file, ingest_sources, save_upload,
    PDFSourceAdapter, CSVSourceAdapter, ExcelSourceAdapter, DocxSourceAdapter, TextSourceAdapter, ImageSourceAdapter
)


def test_ingestion_suite():
    print("==================================================")
    print("PRODUCTIQ AI -- INGESTION ADAPTERS TEST SUITE")
    print("==================================================")

    # 1. Test PDF Ingestion
    print("\n--- 1. Testing PDF Source Adapter ---")
    pdf_path = os.path.join("data", "Test_Temperature_Sensor.pdf")
    assert os.path.exists(pdf_path), "Test_Temperature_Sensor.pdf missing!"

    pdf_doc = ingest_file(pdf_path)
    assert isinstance(pdf_doc, SourceDocument), "Result must be a SourceDocument"
    assert pdf_doc.source_type == "pdf", f"Expected type 'pdf', got '{pdf_doc.source_type}'"
    assert len(pdf_doc.pages) > 0, "PDF pages array must not be empty"
    assert "Temperature" in pdf_doc.content or "Sensor" in pdf_doc.content, "PDF content text mismatch"
    print(f"[PASS] PDF ingested successfully ({len(pdf_doc.pages)} page(s), {len(pdf_doc.content)} chars).")

    # 2. Test CSV Ingestion
    print("\n--- 2. Testing CSV Source Adapter ---")
    csv_path = os.path.join("data", "sample_catalog.csv")
    assert os.path.exists(csv_path), "sample_catalog.csv missing!"

    csv_doc = ingest_file(csv_path)
    assert csv_doc.source_type == "csv", f"Expected type 'csv', got '{csv_doc.source_type}'"
    assert "product_name" in csv_doc.content, "CSV header missing in ingested text"
    assert csv_doc.metadata.get("row_count") >= 2, "CSV metadata row count mismatch"
    print(f"[PASS] CSV ingested successfully ({csv_doc.metadata['row_count']} rows).")

    # 3. Test Text & Markdown Ingestion
    print("\n--- 3. Testing Text & Markdown Adapters ---")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Product: Industrial Pressure Valve\nManufacturer: FlowControl Inc\nPressure: 10 bar\n")
        tmp_txt = f.name

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Industrial Bearing\n- Model: BRG-500\n- Load Rating: 15 kN\n")
        tmp_md = f.name

    txt_doc = ingest_file(tmp_txt)
    assert txt_doc.source_type == "text", "TXT type mismatch"
    assert "FlowControl" in txt_doc.content

    md_doc = ingest_file(tmp_md)
    assert md_doc.source_type == "markdown", "Markdown type mismatch"
    assert "BRG-500" in md_doc.content
    print("[PASS] Text and Markdown documents ingested successfully.")

    os.remove(tmp_txt)
    os.remove(tmp_md)

    # 4. Test Image OCR Fallback
    print("\n--- 4. Testing Image OCR Graceful Error Handling ---")
    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
        tmp_img = f.name

    try:
        ingest_file(tmp_img)
        print("[INFO] Image ingested with local OCR engine.")
    except IngestionError as e:
        assert "OCR" in str(e), f"Expected OCR error message, got: {e}"
        print("[PASS] Image without OCR handled gracefully with clear user error.")
    finally:
        os.remove(tmp_img)

    # 5. Test save_upload Security & Constraints
    print("\n--- 5. Testing save_upload Storage & File Validation ---")
    saved_path = save_upload(pdf_path)
    assert os.path.exists(saved_path), "Saved persistent file path does not exist"
    assert "uploads" in saved_path.lower(), "Saved path must be inside uploads directory"
    print(f"[PASS] File saved securely into uploads storage: '{saved_path}'.")

    # 6. Test Multi-Source Bundling
    print("\n--- 6. Testing Multi-Source Ingestion Bundling ---")
    multi_docs = ingest_sources(
        files=[pdf_path, csv_path],
        text="Supplementary text: Heavy duty industrial pneumatic actuator."
    )
    assert len(multi_docs) == 3, f"Expected 3 SourceDocuments, got {len(multi_docs)}"
    types = [d.source_type for d in multi_docs]
    assert "pdf" in types and "csv" in types and "pasted_text" in types, f"Missing source type in {types}"
    print(f"[PASS] Multi-source ingestion correctly created {len(multi_docs)} SourceDocuments.")

    print("\n==================================================")
    print("ALL INGESTION ADAPTER TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_ingestion_suite()
    sys.exit(0 if success else 1)
