# ProductIQ AI Evaluation & Benchmark System Audit

## 1. Executive Summary
This document provides a comprehensive audit of the ProductIQ AI intelligence pipeline to prepare for Phase 4: AI Evaluation, Benchmarking, and Quality Analytics. It defines what can be evaluated deterministically, what requires independent gold-standard ground truth, and establishes mathematical formulations for all judge-facing evaluation metrics.

---

## 2. Current Architecture Review

### 2.1 Extraction Pipeline (`backend/extraction.py`, `backend/pipeline.py`)
- **Ingestion & Text Assembly**: Ingests PDFs (PyMuPDF / pdfplumber), Web URLs (trafilatura / BeautifulSoup), CSV/XLSX (pandas/openpyxl), DOCX (python-docx), and plain text.
- **LLM Structured Extraction**: Interfaces with local Ollama (`llama3.2:3b`) using strict JSON schema prompting.
- **Current Behavior**: Extracts `product_name`, `manufacturer`, `product_code`, `category`, `description`, specifications `[name, value, unit, page]`, and enrichment metadata.

### 2.2 Evidence Grounding & Anti-Hallucination (`backend/evidence.py`)
- **Verbatim Isolation**: Deterministically scans source text lines to find verbatim citations for extracted attributes.
- **Status Classification**:
  - `VERIFIED`: Attribute name and value found verbatim in source text.
  - `PARTIALLY_VERIFIED`: Value or unit located, or attribute label found.
  - `NOT_FOUND`: No grounding in supplied sources (triggers anti-hallucination penalty).
- **Evidence Types**: `DIRECT`, `TABLE`, `MULTI_SOURCE`, `AI_ENRICHED`, `INFERRED`, `UNVERIFIED`.

### 2.3 Unit Normalization Engine (`backend/normalization.py`)
- **Physical Equivalences**:
  - Pressure: `1 MPa == 10 bar == 1000 kPa`
  - Dimensions: `1000 mm == 1 m == 100 cm`
  - Mass: `1000 g == 1 kg`
  - Power: `1 kW == 1000 W`
  - Temperature: `-20 to 80 °C == -20-80 °C`
- **Rule Tracking**: Records `normalization_applied` and `normalization_rule`.

### 2.4 Confidence Scoring (`backend/confidence.py`)
- **Multi-Factor Scoring (0–100%)**:
  - Value completeness (20%)
  - Evidence citation score (35%)
  - Page attribution (15%)
  - Source reliability weighting (30%): `OFFICIAL_DATASHEET` (1.0), `OFFICIAL_WEBSITE` (0.95), `MANUFACTURER_CATALOG` (0.90), `DISTRIBUTOR` (0.75), `THIRD_PARTY` (0.60), `USER_INPUT` (0.50), `AI_INFERENCE` (0.30).
  - Validation warning penalty (-20%) and conflict penalty (-30%).

### 2.5 Conflict Detection & Resolution (`backend/conflicts.py`, `backend/database/repositories/conflict_repository.py`)
- **Classification**: `VALUE_MISMATCH`, `UNIT_MISMATCH`, `MISSING_VALUE`, `DUPLICATE_ATTRIBUTE`, `IDENTITY_CONFLICT`, `CATEGORY_CONFLICT`.
- **Severity**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- **Resolution**: 6 resolution actions with immutable versioning (`v1` -> `v2`) and audit logging.

### 2.6 Quality Score & Commerce Readiness (`backend/scoring.py`)
- **Quality Score (0–100%)**:
  - Completeness (25%)
  - Extraction Quality (25%)
  - Validation Quality (20%)
  - Evidence Coverage (15%)
  - Consistency (15%)
- **Commerce Readiness Status**: `READY_FOR_COMMERCE`, `REVIEW_REQUIRED`, `NOT_READY`, `HUMAN_VERIFIED`. Open `CRITICAL` or `HIGH` conflicts strictly force `REVIEW_REQUIRED`.

---

## 3. Evaluation Scope & Measurement Boundary

### 3.1 Deterministically Measurable
- Attribute name matching (case/symbol insensitive).
- Normalized value & unit equivalence comparison.
- Evidence citation presence and page location match.
- Hallucination detection on negative control attributes.
- Validation rule trigger accuracy (PASS / FAIL / WARNING / REVIEW).
- Conflict detection precision, recall, and severity alignment.
- Commerce readiness state transitions.
- Confidence calibration across 4 probability bins (`0-49`, `50-69`, `70-89`, `90-100`).

### 3.2 Requiring Benchmark Ground Truth
- Field-level completeness against actual manufacturer datasheets.
- True positive, false positive, and false negative attribute extraction counts.
- Extraction precision, recall, and F1 across diverse product categories.
- Negative test verification (attributes intentionally omitted in source text).

---

## 4. Benchmark Architecture Plan
- **Dataset Structure**: `data/benchmark/`
  - `sources/`: Source documents/fixtures for 10 distinct industrial product categories.
  - `ground_truth/`: Machine-readable JSON specifications containing exact verified facts and negative hallucination probes.
  - `baseline.json`: Versioned baseline metrics for regression detection.
- **Persistent Evaluation Runs**: Database entities (`EvaluationRunEntity`, `EvaluationProductResultEntity`, `EvaluationMetricEntity`) storing test outputs, confusion matrices, and quality gate evaluations.
