# Human Review Audit & Versioning Log

## 1. Purpose & Standards
In industrial commerce, changes to technical specifications (e.g. pressure ratings, electrical tolerances) carry significant engineering liability. ProductIQ AI provides cryptographically immutable audit trails for every manual modification, conflict resolution, or attribute dismissal.

---

## 2. Audit Record Fields

- `audit_id`: Unique identifier for the audit event.
- `product_id`: Associated catalog product.
- `version_id`: Product version created or modified.
- `conflict_id`: Associated cross-source conflict if resolving a discrepancy.
- `attribute_name`: Technical parameter modified.
- `previous_value`: Value prior to human action.
- `new_value`: Adjudicated value confirmed by engineer.
- `action`: Resolution action code (`USE_SOURCE_A`, `USE_SOURCE_B`, `MANUAL_OVERRIDE`, `KEEP_BOTH`, `DISMISS`).
- `reason`: Mandatory rationale provided by the engineer.
- `reviewer`: Identifier/username of the engineer performing the review.
- `created_at`: UTC timestamp of the action.
