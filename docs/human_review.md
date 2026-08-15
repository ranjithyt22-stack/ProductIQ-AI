# Human Review & Resolution Center Architecture

## Overview
The Human Review Center provides industrial commerce teams with full human-in-the-loop control over cross-source discrepancies, parameter overrides, and commerce qualification.

---

## 1. Human Resolution Actions
When inspecting a conflict, reviewers can choose from 6 explicit resolution pathways:

1. **`USE_SOURCE_A`**: Selects Source A's reported value and unit as canonical.
2. **`USE_SOURCE_B`**: Selects Source B's reported value and unit as canonical.
3. **`ENTER_CORRECT_VALUE`**: Human engineer provides verified value, unit, and reason.
4. **`KEEP_BOTH`**: Retains both values in application notes or alternative operating conditions.
5. **`MARK_UNRESOLVED`**: Leaves the conflict active in the review queue for senior engineering verification.
6. **`DISMISS_CONFLICT`**: Dismisses non-actionable or cosmetic variances without blocking publication.

---

## 2. Immutable Versioning on Resolution
When a human reviewer resolves a conflict or modifies a parameter:
- The previous product version remains completely immutable in the database.
- A new product version (e.g. `v2`, `v3`) is created automatically.
- The resolved specification is updated with:
  - `review_status = "human_verified"`
  - `confidence = 100.0`
  - `review_required = False`
  - `match_status = "VERIFIED"`
- The quality score and commerce readiness status are re-evaluated.

---

## 3. Immutable Resolution Audit Trail
Every review action generates an append-only audit record (`ReviewAuditEntity`) containing:
- `audit_id` (Unique identifier)
- `product_id` and `version_id`
- `attribute_name`
- `reviewer` (Reviewer identity)
- `action` (Selected resolution action)
- `old_value` and `new_value`
- `reason` and `notes`
- `timestamp` (ISO 8601 UTC timestamp)

---

## 4. REST v1 API Endpoints
- `GET /api/v1/products/{product_id}/conflicts`: Query conflicts for a specific product.
- `GET /api/v1/products/{product_id}/conflicts/{conflict_id}`: Retrieve side-by-side comparison details.
- `POST /api/v1/products/{product_id}/conflicts/{conflict_id}/resolve`: Resolve conflict, produce version `v(N+1)`, and record audit log.
- `GET /api/v1/reviews`: List global review queue across all products with filtering.
- `GET /api/v1/reviews/{review_id}`: Inspect single review item.
- `POST /api/v1/reviews/{review_id}/resolve`: Resolve review item.
- `GET /api/v1/reviews/audits/history`: Query immutable audit history.
