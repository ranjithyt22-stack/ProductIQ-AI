# Automated Testing Guide

ProductIQ AI includes 10 automated test suites verifying all core functionality, security, UI stability, REST API integrity, and end-to-end workflows.

## Test Suite Inventory

| Test File | Target Module | Scope & Verification |
| :--- | :--- | :--- |
| `test_ingestion.py` | `backend/ingestion/` | Ingestion adapters (PDF, CSV, Excel, DOCX, TXT, MD, Image OCR), save_upload security |
| `test_pdf_upload.py` | `app.py`, `backend/pipeline.py` | Non-flickering upload handler, persistent copying, filename isolation, fast execution |
| `test_url_ingestion.py` | `backend/ingestion/web.py` | Web scraping, SSRF security guards, URL validation, timeout error handling |
| `test_validation.py` | `backend/validation.py` | 8-category deterministic validation check rules, sanity ranges, duplicates, conflicts |
| `test_evidence.py` | `backend/evidence.py`, `confidence.py` | Verbatim quote snippet isolation, page attribution, confidence scoring (0-100%) |
| `test_catalog.py` | `backend/catalog.py` | Batch catalog processing, dynamic PIQ-ID generation, fault isolation, exports, search |
| `test_api.py` | `backend/api.py` | FastAPI endpoints, schema validation (422), health checks, catalog/product lookups |
| `test_gradio_events.py` | `app.py` | Gradio component structure, non-flickering output counts (2 outputs), state management |
| `test_end_to_end.py` | Full Application | Complete 10-step hackathon demo flow integration test |

## Running Tests

Execute all tests in sequence using the local virtual environment:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -c "import py_compile, glob; [py_compile.compile(f) for f in glob.glob('*.py') + glob.glob('backend/*.py') + glob.glob('backend/ingestion/*.py')]"
.venv\Scripts\python.exe test_ingestion.py
.venv\Scripts\python.exe test_pdf_upload.py
.venv\Scripts\python.exe test_url_ingestion.py
.venv\Scripts\python.exe test_validation.py
.venv\Scripts\python.exe test_evidence.py
.venv\Scripts\python.exe test_catalog.py
.venv\Scripts\python.exe test_api.py
.venv\Scripts\python.exe test_gradio_events.py
.venv\Scripts\python.exe test_end_to_end.py
```
