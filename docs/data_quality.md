# Product Data Quality Operations

## 1. Overview
ProductIQ AI tracks continuous data quality metrics across the entire product catalog to prevent corrupted or ungrounded data from reaching commerce channels.

---

## 2. Key Metrics & Definitions

- **Average Quality Score**: Composite mathematical health score calculated across attribute completeness, verbatim evidence coverage, validation pass rate, and conflict count.
- **Evidence Coverage Rate**: Percentage of technical parameters backed by direct verbatim source text citations.
- **Validation Rule Pass Rate**: Percentage of numerical specifications adhering to physical range and sanity checks.
- **Conflict Backlog**: Total count of active, unadjudicated supplier discrepancies.

---

## 3. Defect Categories & Remediation Pathways

| Defect Category | Severity | Detection Mechanism | Remediation |
| :--- | :--- | :--- | :--- |
| Missing Required Product Code | CRITICAL | Schema validation check on product identity | Manual entry or source re-extraction |
| Unresolved Cross-Source Conflict | HIGH | Multi-source alignment engine | Adjudicate in Review Center |
| Ungrounded AI Attributes | MEDIUM | Anti-hallucination citation scan | Provide supplier datasheet or human verification |
