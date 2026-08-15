# ProductIQ AI - Phase 2 Evidence Grounding, Confidence & Explainability Audit

## 1. Executive Summary
This document provides a comprehensive audit of the current evidence extraction, attribute confidence scoring, deterministic validation, normalization, and explainability systems within ProductIQ AI. It outlines the architectural baseline established in Phase 1 and defines the roadmap for Phase 2: Evidence-Grounded AI, Attribute-Level Confidence, and Explainability.

---

## 2. Current Evidence Implementation
- **Module**: `backend/evidence.py` (`isolate_evidence`)
- **Mechanism**: Iterates over page text lines, performing substring matching on extracted attribute values and token-overlap matching on attribute names.
- **Output**: Returns `(page_number, snippet, match_score)`.
- **Limitations**:
  - Treats evidence as a secondary string snippet rather than a first-class source-backed object with explicit classification types (`DIRECT`, `TABLE`, `MULTI_SOURCE`, `AI_ENRICHED`, `INFERRED`, `UNVERIFIED`).
  - Lacks strict anti-hallucination rejection when the LLM extracts an attribute unmentioned in the source.
  - Does not distinguish between manufacturer datasheets and third-party or user-supplied text when assessing evidence veracity.

---

## 3. Current Confidence Implementation
- **Module**: `backend/confidence.py` (`calculate_attribute_confidence`)
- **Mechanism**: Additive heuristic scoring starting at base 40, awarding points for page presence (+10), evidence score (+25), unit presence (+15), and deducting points for validation warnings (-15) and inferred status (-20).
- **Limitations**:
  - Lacks source reliability weighting (`OFFICIAL_DATASHEET`, `OFFICIAL_WEBSITE`, `MANUFACTURER_CATALOG`, `DISTRIBUTOR`, `THIRD_PARTY`, `USER_INPUT`, `AI_INFERENCE`).
  - Does not factor in cross-source agreement/conflict directly into the confidence calculation per attribute.
  - Lacks explicit confidence tiers (`HIGH`: 90-100, `MEDIUM`: 70-89, `LOW`: 50-69, `UNVERIFIED`: 0-49).

---

## 4. Current Validation Flow
- **Module**: `backend/validation.py` (`validate_product_data`)
- **Coverage**: 8 deterministic rule categories (required metadata, numerical ranges, physical limits, unit standards, duplicate attributes, format consistency, empty attributes, multi-source conflicts).
- **Integration**: Feeds into `ValidationResult` entities and general quality scoring, but does not yet emit structured "Why Review is Required" diagnostic explanations for individual attributes.

---

## 5. Current Database Relationships & Persistence
- **ORM Entities** (`backend/database/models.py`):
  - `ProductEntity` (1 -> N `ProductVersionEntity`, 1 -> N `ProductSourceEntity`)
  - `ProductVersionEntity` (1 -> N `ProductSpecificationEntity`, 1 -> N `ValidationRecordEntity`, 1 -> 1 `EnrichmentRecordEntity`, 1 -> 1 `QualityScoreEntity`, 1 -> N `HumanReviewEntity`)
  - `ProductSpecificationEntity` (1 -> 1 `EvidenceRecordEntity`)
- **Persistence State**: Complete SQLite persistence with SQLAlchemy 2.0. Database schema is clean, robust, and extensible.

---

## 6. Current Frontend Evidence Display
- **Components**:
  - `frontend/src/components/Specifications.jsx`: Renders tabular attribute names, values, units, confidence %, page numbers, validation status, and review status.
  - `frontend/src/components/EvidencePanel.jsx`: Dropdown selector displaying verbatim snippet and page number.
- **Limitations**:
  - Does not allow clicking on a specification row to inspect attribute-level intelligence, normalization rules, and validation reasons in an interactive drawer.
  - Does not separate evidence visually into distinct buckets: Verified Source Facts, AI-Enriched Information, Unverified Information, and Conflicting Information.
  - Does not render a visual step-by-step Data Lineage graph component (`frontend/src/components/DataLineage.jsx`).

---

## 7. Identified Gaps & Weaknesses
1. **Anti-Hallucination Rejection**: LLM hallucinations without source backing must be explicitly rejected (`value = null` or unverified flag, `status = UNVERIFIED`, `review_required = true`).
2. **First-Class Evidence Model**: Evidence records must support source classification, match status (`VERIFIED`, `PARTIALLY_VERIFIED`, `NOT_FOUND`, `CONFLICTING`, `UNVERIFIED`), and explicit evidence types (`DIRECT`, `TABLE`, `MULTI_SOURCE`, `AI_ENRICHED`, `INFERRED`, `UNVERIFIED`).
3. **Source Reliability Hierarchy**: Configurable source trust weights must influence confidence scoring.
4. **Normalization Transparency**: The system must track and expose `raw_value`, `normalized_value`, `normalization_applied`, and `normalization_rule`.
5. **Structured Explainability Record**: Complete attribute-level explainability record explaining exactly why a value was accepted, normalized, or flagged for review without exposing raw LLM chain-of-thought.
6. **Commerce Readiness Determinism**: Strict criteria where products with missing critical attributes, unverified facts, or unresolved conflicts cannot be marked `READY_FOR_COMMERCE`.

---

## 8. Implementation Plan for Phase 2
- **Phase 2.1: Model & Schema Enhancements**: Expand `EvidenceRecord`, `SpecificationAttribute`, `ExplainabilityRecord`, and database schemas with first-class fields and evidence types.
- **Phase 2.2: Deterministic Evidence Verification & Anti-Hallucination Engine**: Enhance `backend/evidence.py` and `backend/extraction.py` to strictly verify citations and reject hallucinations.
- **Phase 2.3: Configurable Source Reliability & Attribute Confidence Engine**: Refactor `backend/confidence.py` with multi-factor weighted confidence models and threshold tiers.
- **Phase 2.4: Normalization Lineage & Rule Tracking**: Upgrade `backend/normalization.py` to record applied transformation rules.
- **Phase 2.5: Explainability Engine & Structured Reasoning**: Build `backend/explainability.py` generating attribute explainability records with structured "Why Review" diagnostics.
- **Phase 2.6: Commerce Readiness & Quality Scoring**: Update `backend/scoring.py` with deterministic readiness gating.
- **Phase 2.7: REST API v1 Enhancements**: Expose `/api/v1/products/{id}/evidence`, `/api/v1/products/{id}/confidence`, `/api/v1/products/{id}/explainability`, and `/api/v1/products/{id}/validation`.
- **Phase 2.8: React Frontend Components**:
  - Create `frontend/src/components/AttributeIntelligence.jsx`.
  - Create `frontend/src/components/DataLineage.jsx`.
  - Upgrade `frontend/src/components/EvidencePanel.jsx` (4 evidence buckets).
  - Upgrade `frontend/src/components/Specifications.jsx` (clickable rows opening Attribute Intelligence).
  - Upgrade `frontend/src/pages/ProductAnalyzer.jsx`.
- **Phase 2.9: Automated Test Suites & Regression Verification**:
  - Implement test suites for evidence grounding, confidence, explainability, normalization, anti-hallucination, and commerce readiness across 5 distinct industrial product categories.
  - Run full regression suite and zero-emoji scanner.
