# AI Evaluation & Quality Analytics Architecture

## 1. Overview
ProductIQ AI incorporates a rigorous, deterministic benchmarking and evaluation suite designed to provide quantifiable, defensible proof of intelligence extraction accuracy, anti-hallucination compliance, and commerce readiness qualification across industrial product domains.

---

## 2. Core Evaluation Metrics

| Metric | Mathematical Definition | Target Gate |
|---|---|---|
| **Extraction Precision** | $P = \frac{TP}{TP + FP}$ | $\ge 85.0\%$ |
| **Extraction Recall** | $R = \frac{TP}{TP + FN}$ | $\ge 85.0\%$ |
| **Extraction F1** | $F_1 = \frac{2 \cdot P \cdot R}{P + R}$ | $\ge 85.0\%$ |
| **Value Accuracy** | $\frac{\text{Normalized Equivalence Matches}}{\text{Matched Attributes}}$ | $\ge 85.0\%$ |
| **Unit Accuracy** | $\frac{\text{Compatible Physical Units}}{\text{Matched Attributes}}$ | $\ge 90.0\%$ |
| **Evidence Coverage** | $\frac{\text{Grounded Attributes (DIRECT / TABLE / MULTI\_SOURCE)}}{\text{Total Extracted Attributes}} \times 100$ | $\ge 80.0\%$ |
| **Hallucination Rate** | $\frac{\text{Fabricated / Ungrounded Attributes}}{\text{Total Generated Attributes}} \times 100$ | $\le 5.0\%$ |
| **Validation F1** | $F_1 \text{ against expected validation checks}$ | $\ge 85.0\%$ |
| **Conflict Detection F1** | $F_1 \text{ on multi-source discrepancies}$ | $\ge 85.0\%$ |
| **Commerce Readiness Accuracy** | $\frac{\text{Correct Commerce Readiness Predictions}}{\text{Total Products}} \times 100$ | $\ge 85.0\%$ |
| **Confidence Calibration** | $100 - \sum \frac{N_b}{N} |\text{acc}_b - \text{conf}_b| \times 100$ | $\ge 80.0\%$ |

---

## 3. Anti-Hallucination & Negative Control Probing
To ensure the LLM never invents ungrounded specifications, the benchmark includes negative test cases containing attributes explicitly omitted from the manufacturer source document (e.g. warranty periods, explosion-proof ratings). The evaluation engine verifies that these are strictly classified as `NOT_FOUND` or `UNVERIFIED` with zero confidence.

---

## 4. REST v1 Evaluation Endpoints
- `POST /api/v1/evaluations/run`: Trigger benchmark run across the gold-standard dataset.
- `GET /api/v1/evaluations`: List historical benchmark runs with scores and quality gate status.
- `GET /api/v1/evaluations/{id}`: Detailed summary of a single evaluation.
- `GET /api/v1/evaluations/{id}/metrics`: Categorized metrics breakdown.
- `GET /api/v1/evaluations/{id}/products`: Per-product precision, recall, value accuracy, and evidence coverage.
- `GET /api/v1/evaluations/{id}/report`: Structured executive evaluation report.
- `GET /api/v1/evaluations/{id}/confusion-matrix`: Commerce readiness confusion matrix and calibration bins.
- `GET /api/v1/evaluations/baseline/compare`: Regression comparison against verified baseline.
