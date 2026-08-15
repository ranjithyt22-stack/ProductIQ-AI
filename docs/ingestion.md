# Multi-Source Ingestion System Documentation

## Overview
ProductIQ AI features a modular source ingestion framework supporting multi-source input combinations (e.g. Product Page URL + Datasheet PDF + Supplementary Text).

## Supported Formats & Adapters

| Source Type | Extension / Input | Adapter Module | Features |
| :--- | :--- | :--- | :--- |
| **PDF** | `.pdf` | `backend/ingestion/pdf.py` | Page-by-page extraction, document metadata, page numbers |
| **Web Page** | `http://`, `https://` | `backend/ingestion/web.py` | SSRF protection, HTML cleaning, table & spec parsing |
| **CSV Catalog**| `.csv` | `backend/ingestion/csv.py` | Dynamic column mapping, header detection, fault isolation |
| **Excel** | `.xlsx`, `.xls` | `backend/ingestion/excel.py` | Multi-sheet reading via `openpyxl` & `pandas` |
| **DOCX** | `.docx` | `backend/ingestion/docx.py` | Headings, paragraphs, table rows via `python-docx` |
| **Text / MD** | `.txt`, `.md` | `backend/ingestion/text.py` | Unstructured text ingestion |
| **Images** | `.png`, `.jpg` | `backend/ingestion/image.py` | Local OCR fallback handling |

## SSRF Security Protection
Web URL ingestion (`backend/ingestion/web.py`) enforces strict Server-Side Request Forgery (SSRF) checks:
- Accepts only `http` and `https` schemes.
- Blocks `localhost`, `127.0.0.1`, `0.0.0.0`, `::1`.
- Resolves DNS hostname and checks IP addresses against non-global/private ranges (`10.x`, `172.16-31.x`, `192.168.x`, `169.254.x.x`).
- Implements strict request timeout (`12s`) and content size limits (`2 MB`).

## Provenance & Multi-Source Conflict Detection
When combining multiple sources (e.g., PDF + URL), ProductIQ AI attaches `source_id`, `source_name`, `source_type`, and `source_uri` to every extracted specification attribute.
If Source A (PDF) specifies `Pressure = 10 bar` and Source B (URL) specifies `Pressure = 12 bar`, the pipeline logs a **Multi-Source Conflict Check** alert, flags the attribute status as `REQUIRES MANUAL REVIEW`, and prevents silent overwriting.
