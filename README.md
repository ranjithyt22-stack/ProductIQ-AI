# ProductIQ AI

> **AI-Powered Product Intelligence for Industrial Commerce & Scalable Catalog Engine**  
> *Zero-Cost, Multi-Source Industrial Data Normalization, Validation, Evidence Traceability & AI Intelligence Platform*

---

## Problem Statement

Industrial companies manage large amounts of product information across scattered sources: websites, PDF datasheets, catalogs, technical spreadsheets, Word documents, images, and raw text descriptions. Converting this unstructured, multi-source data into accurate, normalized, validated, explainable, and commerce-ready product data is difficult and time-consuming. Traditional AI approaches suffer from hallucination of technical specifications and lack evidence traceability.

## Solution

**ProductIQ AI** is a zero-cost, enterprise-grade Product Intelligence platform that converts unstructured, multi-source industrial inputs into normalized, validated, evidence-backed, and commerce-ready product intelligence.

### Key Capabilities:
1. **Multi-Source Data Ingestion**: Accepts PDFs, Website URLs, CSV catalogs, Excel spreadsheets (`.xlsx`/`.xls`), Word documents (`.docx`), plain text (`.txt`/`.md`), pasted text, and images.
2. **Multi-Source Combination & Provenance**: Combines product page URLs with supplementary PDFs and pasted text while tracking source provenance for every attribute.
3. **Multi-Source Conflict Detection**: Identifies conflicting specifications across different sources (e.g. PDF says pressure=10 bar vs Website says 12 bar) and flags them for manual review.
4. **Strict Anti-Hallucination AI Extraction**: Uses local Ollama (`llama3.2:3b`) with strict JSON schema constraints to prevent model hallucination.
5. **Deterministic Unit Normalization**: Standardizes technical units (`millimeters` to `mm`, `kilograms` to `kg`, `degrees Celsius` to `degC`, `bar`, `V`, `A`, `kW`, `m/s`, `rpm`).
6. **8-Category Validation Engine**: Checks required fields, unit consistency, numeric range sanity, duplicate attributes, missing data, engineering consistency, and cross-source conflicts.
7. **Verbatim Evidence Traceability**: Pinpoints exact verbatim sentence quotes and page/source attribution for 100% explainable AI.
8. **Deterministic Confidence Scoring**: Calculates 0-100% confidence scores based on page attribution, verbatim snippet score, unit validity, and validation flags.
9. **Source Facts vs AI Enrichment**: Clearly distinguishes manufacturer source facts from AI-generated search terms, taxonomy paths, and applications.
10. **Product Quality Readiness Score**: Computes an overall score (0-100) and categorizes readiness into `READY FOR COMMERCE` (90-100), `REVIEW RECOMMENDED` (70-89), or `REQUIRES MANUAL REVIEW` (<70).
11. **Human Review & Verification**: Enables human-in-the-loop overrides and updates spec status to `HUMAN VERIFIED`.
12. **Scalable Catalog Engine**: Sequential batch orchestrator with per-product fault isolation. One failing catalog item will never crash the batch.
13. **Modern React + Vite Frontend**: Responsive Dark Navy industrial dashboard with zero-flicker state isolation and Lucide SVG icons.
14. **FastAPI REST API & Swagger UI**: Complete REST endpoints with OpenAPI docs.
15. **100% Zero-Cost Local Execution**: Operates locally using Ollama inference without paid cloud API keys.

---

## REST API Endpoints

- `GET /health` - System liveness & local Ollama health check
- `POST /analyze` - Single product extraction & analysis endpoint
- `POST /analyze/url` - Dedicated web URL product extraction endpoint
- `POST /analyze/file` - Dedicated document file (PDF/DOCX/CSV/XLSX/TXT) analysis endpoint
- `POST /analyze/text` - Dedicated raw text description analysis endpoint
- `POST /analyze/multi-source` - Combined multi-file, multi-URL, text analysis endpoint
- `POST /validate` - Standalone 8-category validation check endpoint
- `POST /enrich` - Taxonomy & search enrichment endpoint
- `POST /catalog/analyze` - Batch catalog CSV ingestion endpoint
- `GET /catalog/{catalog_id}` - Catalog batch result retrieval endpoint
- `GET /product/{product_id}` - Single product intelligence record lookup endpoint
- `POST /product/{product_id}/review` - Human review attribute override endpoint
- `GET /product/{product_id}/export/json` - Export product JSON record
- `GET /product/{product_id}/export/csv` - Export product specifications CSV

*Interactive Swagger UI*: `http://localhost:8000/docs`

---

## Technology Stack

- **Frontend**: React 18, Vite, Lucide React (Zero Emojis, Dark Navy Industrial Theme)
- **Backend Runtime**: Python 3.10+
- **REST API**: FastAPI, Uvicorn, Pydantic
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`, `pandas`, `openpyxl`
- **Web Scraping & SSRF Protection**: `httpx`, `BeautifulSoup4`, `socket`, `ipaddress`
- **AI Inference Engine**: Local Ollama (`llama3.2:3b`)
- **Fallback UI**: Gradio 4.x

---

## Running Locally

### 1. Prerequisites
Ensure Python 3.10+, Node.js 18+, and [Ollama](https://ollama.com/) are installed.

### 2. Pull the Local Model
```bash
ollama pull llama3.2:3b
```

### 3. Start Backend API Server
```powershell
.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```
*API running at `http://127.0.0.1:8000` | OpenAPI docs at `http://127.0.0.1:8000/docs`*

### 4. Start React Frontend
```powershell
cd frontend
npm install
npm run dev
```
*Frontend running at `http://localhost:5173`*

---

## Running Automated Tests

Run the complete regression test suite:

```powershell
# Run zero-emoji scanner
.\.venv\Scripts\python.exe test_no_emojis.py

# Run full pytest suite across all modules
.\.venv\Scripts\python.exe -m pytest . -v

# Run frontend production build
npm --prefix frontend run build
```

---

## Enterprise Workspaces (Phase 5)

1. **Executive Overview**: High-level telemetry, KPI summary, and active audit stream.
2. **Product Analyzer**: Source workspace for PDF, URL, DOCX, CSV, and text ingestion with deterministic extraction and side-drawer attribute intelligence.
3. **Catalog Engine**: Bulk spreadsheet processing, fault-isolated batches, and product inspector.
4. **Review Center**: Triage queue for cross-source supplier discrepancies with 6 resolution pathways.
5. **Data Quality Operations**: Systemic defect monitoring and attribute completeness tracking.
6. **AI Evaluation & Benchmarking**: 10-product gold-standard benchmark suite with precision, recall, F1, calibration buckets, confusion matrices, and regression detection.
7. **AI Governance**: Model registry, prompt template versioning, and zero-cost local compliance.
8. **Global Search**: Multi-attribute filtering across stored catalog records.
9. **System Health**: Telemetry on API server, relational storage, and local Ollama inference.
10. **Audit Log**: Cryptographically recorded provenance for all human actions.

.venv\Scripts\python.exe test_pdf_upload.py
.venv\Scripts\python.exe test_url_ingestion.py
.venv\Scripts\python.exe test_validation.py
.venv\Scripts\python.exe test_evidence.py
.venv\Scripts\python.exe test_catalog.py
.venv\Scripts\python.exe test_api.py
.venv\Scripts\python.exe test_source_isolation_regression.py
.venv\Scripts\python.exe test_end_to_end.py
```