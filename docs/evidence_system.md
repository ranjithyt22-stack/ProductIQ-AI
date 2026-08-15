# ProductIQ AI: Evidence-Grounded AI, Attribute Confidence & Explainability Architecture (Phase 2)

## 1. System Overview & Core Philosophy

ProductIQ AI is built on a fundamental principle of Industrial Commerce:
**"The platform must never blindly trust an LLM-generated value."**

In industrial equipment procurement, engineering specifications (such as pressure tolerances, bore diameters, voltage ratings, and hazardous area certifications) are mission-critical. A single hallucinated parameter can lead to mechanical failure, safety hazards, or regulatory non-compliance.

ProductIQ AI enforces a deterministic pipeline where all LLM suggestions are rigorously isolated, grounded against verbatim source bytes, normalized with transparent conversion lineages, evaluated against engineering constraints, and assigned multi-factor confidence scores before reaching commerce readiness.

---

## 2. End-to-End Processing Architecture

```
                                      +---------------------------------------------+
                                      | 1. Ingested Sources (PDF, Web, CSV, Excel) |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 2. Raw Content Assembly (Verbatim Pages)    |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 3. Local LLM Structured Extraction (Ollama) |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 4. Transparent Unit Normalization & Lineage |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 5. Deterministic Verbatim Evidence Matching |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 6. Engineering Constraints & Validations    |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 7. Multi-Factor Attribute Confidence Engine |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 8. Structured Explainability & Audit Trail  |
                                      +---------------------------------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      | 9. Commerce Readiness Gating (Deterministic)|
                                      +---------------------------------------------+
                                                             |
                              +------------------------------+------------------------------+
                              |                                                             |
                              v                                                             v
               +-----------------------------+                               +-----------------------------+
               | READY_FOR_COMMERCE (>=80%) |                               | REVIEW_REQUIRED / UNVERIFIED|
               +-----------------------------+                               +-----------------------------+
```

---

## 3. Verbatim Evidence Grounding & Anti-Hallucination

Every extracted parameter is verified against source text using deterministic substring matching, numerical boundary isolation, and citation typing:

### Citation Types (`EvidenceType`)
- `DIRECT`: Exact verbatim quote extracted directly from the manufacturer datasheet.
- `TABLE`: Parameter matched within structured table rows or columns.
- `MULTI_SOURCE`: Parameter verified across 2 or more independent sources.
- `AI_ENRICHED`: Taxonomy classifications, keyword search terms, and suggested applications generated by LLM reasoning (never presented as manufacturer source facts).
- `INFERRED`: Derived engineering values (e.g. converted units).
- `UNVERIFIED`: Values suggested by the LLM that cannot be matched to verbatim text in the provided source documents.

### Anti-Hallucination Rule
If an LLM outputs an attribute (e.g., `Warranty Period = 1 year`) that does not appear in the source text:
- `match_status = MatchStatus.NOT_FOUND`
- `evidence_type = EvidenceType.UNVERIFIED`
- `evidence_confidence = 0.0`
- `confidence = 0` (Tier: `UNVERIFIED`)
- `status = "UNVERIFIED"`
- `review_required = True`
- `review_reason = "Evidence was not found in the supplied sources."`

---

## 4. Multi-Factor Attribute Confidence Scoring Model

Attribute confidence is calculated from 0 to 100 using a deterministic multi-factor formula:

$$Score = \min(100, \max(0, Base \times W_{source} - P_{warning} - P_{conflict} - P_{unit}))$$

### Source Reliability Weights ($W_{source}$)
- `OFFICIAL_DATASHEET`: 1.00
- `OFFICIAL_WEBSITE`: 0.95
- `MANUFACTURER_CATALOG`: 0.90
- `DISTRIBUTOR`: 0.75
- `THIRD_PARTY`: 0.60
- `USER_INPUT`: 0.50
- `AI_INFERENCE`: 0.30

### Penalties
- Missing Unit for numerical attributes: -15
- Engineering Validation Warning (e.g. pressure exceeding typical limit): -30
- Multi-Source Conflict: -40
- Missing Page Citation: -5

### Confidence Tiers
- **HIGH (90 - 100%)**: Verbatim match in official datasheet with recognized units and no warnings.
- **MEDIUM (70 - 89%)**: Matched in distributor catalog, partial match, or inferred unit.
- **LOW (50 - 69%)**: Validation warning or third-party source.
- **UNVERIFIED (0 - 49%)**: No evidence snippet found or conflicting claims across sources.

---

## 5. Transparent Unit Normalization & Lineage Tracking

ProductIQ AI retains the complete lineage of numerical normalization:
1. `raw_value`: The exact string extracted from text (e.g., `"1 to 10 bar"`, `"1 MPa"`, `"24V DC"`).
2. `normalized_value`: The standardized scalar or range (e.g., `"1 to 10"`, `"10"`, `"24"`).
3. `unit`: The canonical SI/industrial unit (e.g., `"bar"`, `"°C"`, `"mm"`, `"kW"`, `"V"`).
4. `normalization_applied`: Boolean flag indicating if conversion or formatting occurred.
5. `normalization_rule`: The deterministic rule executed (e.g. `"convert_unit (1 MPa -> 10 bar)"`, `"extract_range_unit (bar -> bar)"`).

---

## 6. Structured Explainability Records (No LLM Chain-of-Thought)

Explainability records provide full diagnostic reasoning using structured facts without exposing internal LLM prompt strings or chain-of-thought:

```json
{
  "attribute_name": "Operating Pressure",
  "final_value": "1 to 10 bar",
  "raw_value": "1 to 10 bar",
  "normalized_value": "1 to 10",
  "source": "Datasheet.pdf",
  "page": 1,
  "evidence": "Operating pressure range: 1 to 10 bar",
  "evidence_status": "VERIFIED",
  "evidence_type": "DIRECT",
  "normalization_status": "SUCCESS",
  "normalization_rule": "extract_range_unit (bar -> bar)",
  "validation_status": "PASS",
  "cross_source_status": "AGREEMENT",
  "confidence": 97,
  "confidence_level": "HIGH",
  "review_required": false,
  "review_reason": null,
  "final_status": "VERIFIED"
}
```

---

## 7. Deterministic Commerce Readiness Gating

A product is evaluated against 4 deterministic states:

1. `READY_FOR_COMMERCE`:
   - Overall Quality Score >= 80%
   - Evidence Coverage >= 70%
   - Validation Pass Rate >= 80%
   - No unresolved multi-source conflicts
   - Product Identity complete (Name, Manufacturer, SKU)

2. `REVIEW_REQUIRED`:
   - Product contains conflicting source values or unverified attributes.
   - Requires human engineer verification override.

3. `HUMAN_VERIFIED`:
   - Attributes have been reviewed and approved by a human engineer via the Human-in-the-Loop interface.

4. `NOT_READY`:
   - Insufficient specifications (< 2 attributes) or missing core product identity.

---

## 8. REST API v1 Explainability Endpoints

- `GET /api/v1/products/{product_id}/evidence`: Returns all source-grounded evidence records and citations.
- `GET /api/v1/products/{product_id}/explainability`: Returns structured explainability records for all specifications.
- `GET /api/v1/products/{product_id}/confidence`: Returns attribute confidence breakdown and source reliability tiers.
- `GET /api/v1/products/{product_id}/validation`: Returns deterministic validation results and severity counts.
- `GET /api/v1/products/{product_id}/lineage`: Returns the end-to-end 8-stage data lineage graph.

---

## 9. Known Limitations & Safe Operation

1. **Scanned Images Without Text Layer**: Image PDFs require Tesseract OCR. If OCR is unavailable, the ingestion adapter returns a clear diagnostic message without crashing.
2. **Tabular Discrepancies**: Complex multi-page matrix tables with merged cells are parsed via row-by-row correlation. Attributes from irregular tables are marked `PARTIALLY_VERIFIED` to trigger engineer confirmation.
3. **Zero Cost Inference**: All model inference runs strictly locally via Ollama (`llama3.2:3b`) without incurring cloud API costs.
