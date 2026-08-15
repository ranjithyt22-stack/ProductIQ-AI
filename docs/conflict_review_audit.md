# Phase 3 Audit: Cross-Source Conflict Detection & Human Review Workflow

## 1. System Architecture Audit

### 1.1 Current Multi-Source Architecture
- Ingestion is handled via `backend/ingestion/manager.py` which aggregates PDF, URL, DOCX, CSV, Excel, TXT, MD, and image inputs into a collection of `SourceDocument` instances.
- `backend/pipeline.py` ingests multiple sources and concatenates text sections with source headers `--- SOURCE: <name> (<type>) ---`.
- In Phase 2, `_detect_source_conflicts` was introduced as a preliminary validation rule in `pipeline.py`, appending `ValidationResult` items with severity `HIGH` and setting attribute `match_status = MatchStatus.CONFLICTING`.

### 1.2 Current Source Model
- `ProductSourceEntity` in `backend/database/models.py` stores source records with `source_id`, `product_id`, `version_id`, `source_type`, `source_name`, `source_uri`, `source_hash`, `content_preview`, and `metadata_json`.
- `SourceRepository` queries sources by product and version.
- Source reliability enum (`SourceReliability`) provides configurable weights (`OFFICIAL_DATASHEET: 1.0`, `OFFICIAL_WEBSITE: 0.95`, `MANUFACTURER_CATALOG: 0.90`, `DISTRIBUTOR: 0.75`, `THIRD_PARTY: 0.60`, `USER_INPUT: 0.50`, `AI_INFERENCE: 0.30`).

### 1.3 Current Evidence Model
- `EvidenceRecordEntity` and `EvidenceRecord` represent verbatim citations extracted from source pages.
- Citation types: `DIRECT`, `TABLE`, `MULTI_SOURCE`, `AI_ENRICHED`, `INFERRED`, `UNVERIFIED`.
- Match statuses: `VERIFIED`, `PARTIALLY_VERIFIED`, `NOT_FOUND`, `CONFLICTING`.

### 1.4 Current Confidence Model
- `backend/confidence.py` calculates 0-100% scores using source reliability weights, unit validity, verbatim evidence matching, validation penalties (-30), and conflict penalties (-40).
- Confidence tiers: `HIGH (90-100%)`, `MEDIUM (70-89%)`, `LOW (50-69%)`, `UNVERIFIED (0-49%)`.

### 1.5 Current Human Review Model
- `HumanReviewEntity` stores individual attribute overrides with `review_id`, `product_id`, `version_id`, `attribute_name`, `original_value`, `reviewed_value`, `reviewed_unit`, `verification_note`, `status`, and `reviewer_id`.
- `ReviewRepository` provides basic save and query operations for reviews.

### 1.6 Current API Routes
- Existing endpoints:
  - `POST /analyze`, `POST /analyze/file`, `POST /analyze/url`, `POST /analyze/text`, `POST /analyze/multi-source`
  - `POST /validate`, `POST /enrich`
  - `POST /catalog/analyze`, `GET /catalog/{catalog_id}`
  - `GET /product/{product_id}`, `POST /product/{product_id}/review`
  - `GET /api/v1/products`, `POST /api/v1/products`, `GET /api/v1/products/{product_id}`
  - `GET /api/v1/products/{product_id}/versions`, `GET /api/v1/products/{product_id}/versions/compare`
  - `GET /api/v1/products/{product_id}/sources`
  - `GET /api/v1/products/{product_id}/lineage`
  - `GET /api/v1/products/{product_id}/specifications`
  - `GET /api/v1/products/{product_id}/evidence`
  - `GET /api/v1/products/{product_id}/explainability`
  - `GET /api/v1/products/{product_id}/confidence`
  - `GET /api/v1/products/{product_id}/validation`

### 1.7 Current Frontend Review Functionality
- `HumanReview.jsx` renders a review override card on `ProductAnalyzer`.
- `AttributeIntelligence.jsx` contains an embedded review form to mark attributes as `human_verified`.
- No global review queue, dedicated review center, or multi-source conflict diffing workspace currently exists.

---

## 2. Gaps to Be Resolved in Phase 3

| Component | Current State | Phase 3 Requirement |
| :--- | :--- | :--- |
| **Conflict Persistence** | Stored ephemerally as validation warnings | Persistent `ConflictRecordEntity` in DB and `ConflictRepository` with full lifecycle states (`OPEN`, `UNDER_REVIEW`, `RESOLVED`, `DISMISSED`) |
| **Normalized Comparison** | Basic string inequality | Deep normalized comparison supporting unit conversions (`1 MPa == 10 bar`, `1000 mm == 1 m`), whitespace tolerance, and range standardization |
| **Conflict Classification** | Generic conflict flag | 6 typed conflict classes: `VALUE_MISMATCH`, `UNIT_MISMATCH`, `MISSING_VALUE`, `DUPLICATE_ATTRIBUTE`, `IDENTITY_CONFLICT`, `CATEGORY_CONFLICT` |
| **Deterministic Severity** | Static HIGH flag | Deterministic 4-level severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` based on safety, identity, and operating parameters |
| **Conflict Confidence** | Hardcoded penalty | Dynamic calculation based on source reliability, evidence scores, and agreement |
| **Resolution Actions** | Single value replacement | 6 resolution modes: `USE_SOURCE_A`, `USE_SOURCE_B`, `ENTER_CORRECT_VALUE`, `KEEP_BOTH`, `MARK_UNRESOLVED`, `DISMISS_CONFLICT` |
| **Immutable Audit Trail** | Basic review row | Immutable review resolution audit log (`ReviewHistoryEntity` / `ConflictResolutionRecord`) tracking reviewer, old/new values, reason, notes, timestamps |
| **Versioning Integration** | Manual override updates version in memory | Conflict resolution creates a new immutable `ProductVersionEntity` (e.g. `v2`) with detailed change summary |
| **Commerce Gating** | Quality score threshold check | Gated commerce readiness: product is blocked from `READY_FOR_COMMERCE` if unresolved `CRITICAL` or `HIGH` conflicts exist |
| **REST v1 Conflict APIs** | Not implemented | `GET /api/v1/products/{id}/conflicts`, `GET /api/v1/products/{id}/conflicts/{cid}`, `POST /api/v1/products/{id}/conflicts/{cid}/resolve`, `GET /api/v1/reviews`, `GET /api/v1/reviews/{id}`, `POST /api/v1/reviews/{id}/resolve` |
| **Frontend Review Center** | Missing | Dedicated `ReviewCenter.jsx` page with `ReviewQueue.jsx`, `ConflictDetail.jsx`, `ReviewHistory.jsx`, and `ReviewFilters.jsx` |
| **Product Analyzer Integration** | Basic validation warnings | Conflict summary banner, side-by-side comparison, and direct jump to conflict resolution |
| **Data Lineage** | Linear 8-stage sequence | Multi-branch lineage graph showing branching sources merging into conflict resolution and final commerce value |
| **Catalog Integration** | Summary scores only | Aggregated conflict metrics (Products with conflicts, Open conflicts, Critical/High counts) and conflict filtering in catalog table |

---

## 3. Implementation Roadmap

1. **Database & Persistence Layer**:
   - Add `ConflictRecordEntity` and `ReviewAuditEntity` to `backend/database/models.py`.
   - Update `backend/database/connection.py` auto-migration for SQLite tables.
   - Build `ConflictRepository` in `backend/database/repositories/conflict_repository.py`.
   - Upgrade `ReviewRepository` and `ProductRepository`.

2. **Domain Models & Conflict Detection Engine**:
   - Add `ConflictRecord`, `ConflictType`, `ConflictStatus`, `ConflictSeverity`, `ConflictResolutionAction` to `backend/models.py`.
   - Create `backend/conflicts.py` with normalized comparison, unit equivalence checking, conflict classification, severity scoring, and dynamic conflict confidence.
   - Update `backend/pipeline.py` to run `detect_product_conflicts` on all multi-source specifications.
   - Update `backend/scoring.py` to block `READY_FOR_COMMERCE` if open `CRITICAL` or `HIGH` conflicts exist.

3. **REST API v1 Endpoints**:
   - Implement conflict querying, single conflict inspection, conflict resolution, global review queue, and review audit endpoints in `backend/api.py`.

4. **Frontend Review Center & Component Upgrades**:
   - Create `frontend/src/pages/ReviewCenter.jsx`.
   - Create `frontend/src/components/ReviewQueue.jsx`.
   - Create `frontend/src/components/ConflictDetail.jsx`.
   - Create `frontend/src/components/ReviewHistory.jsx`.
   - Create `frontend/src/components/ReviewFilters.jsx`.
   - Update `frontend/src/components/AttributeIntelligence.jsx` with source agreement and conflict inspection.
   - Update `frontend/src/components/DataLineage.jsx` with multi-source branching.
   - Update `frontend/src/pages/ProductAnalyzer.jsx` with conflict badges and conflict resolution drawer.
   - Update `frontend/src/components/CatalogDashboard.jsx` with conflict filtering and health metrics.
   - Update `frontend/src/App.jsx` with Review Center navigation tab.
   - Update `frontend/src/services/api.js` with conflict and review endpoints.

5. **Testing & Quality Assurance**:
   - Build 6 dedicated test suites:
     - `test_conflict_detection.py`
     - `test_conflict_normalization.py`
     - `test_conflict_resolution.py`
     - `test_review_queue.py`
     - `test_review_audit.py`
     - `test_conflict_commerce_readiness.py`
   - Run complete 27-suite regression test.
   - Run `test_no_emojis.py`.
   - Run `npm run build`.
   - Create documentation in `docs/conflict_detection.md` and `docs/human_review.md`.
