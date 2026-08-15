# Quality Metrics & Quality Gate Specification

## 1. Overview
ProductIQ AI enforces quantifiable quality thresholds before industrial products can be qualified as `READY_FOR_COMMERCE` or before a new AI extraction model can pass the regression quality gate.

---

## 2. Quality Gate Thresholds

```json
{
  "min_extraction_f1": 85.0,
  "min_value_accuracy": 85.0,
  "min_unit_accuracy": 90.0,
  "min_evidence_coverage": 80.0,
  "max_hallucination_rate": 5.0,
  "min_validation_f1": 85.0,
  "min_conflict_f1": 85.0,
  "min_commerce_accuracy": 85.0
}
```

A benchmark run status is marked as `PASS` only when every threshold is satisfied.

---

## 3. Composite Product Quality Score
The single-product quality score (0–100%) integrates 5 weighted dimensions:
- **Completeness (25%)**: Mandatory product identity and critical specifications present.
- **Extraction Quality (25%)**: Average confidence across extracted parameters.
- **Validation Quality (20%)**: Absence of engineering rule violations or physical incompatibilities.
- **Evidence Coverage (15%)**: Ratio of source-grounded attributes to total extracted attributes.
- **Consistency (15%)**: Absence of unresolved multi-source discrepancies or conflicting internal statements.
