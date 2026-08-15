# Phase 5: Enterprise-Grade Industrial Product Intelligence UI Architecture

## 1. Executive Summary & Design Philosophy
This document establishes the UI/UX architecture and design system for transforming ProductIQ AI into an industry-grade B2B Industrial Product Intelligence SaaS platform. The design departs entirely from consumer chatbot and generic dashboard aesthetics in favor of an **Industrial Control Center** design language—built for engineering, procurement, catalog operations, and commerce data teams.

---

## 2. Design System Tokens & Color Palette

```css
:root {
  /* Surfaces */
  --bg-primary: #F6F8FA;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #EEF2F5;
  --bg-surface: #FFFFFF;
  --bg-hover: #F1F4F8;
  --bg-active: #E4E9EF;

  /* Typography Colors */
  --text-primary: #17212B;
  --text-secondary: #5B6875;
  --text-muted: #7C8894;
  --text-inverse: #FFFFFF;

  /* Borders & Dividers */
  --border: #D9E0E6;
  --border-strong: #C4CDD6;
  --border-subtle: #E6ECF1;

  /* Brand / Primary */
  --primary: #155EEF;
  --primary-dark: #0B4DB7;
  --primary-light: #EAF2FF;
  --primary-contrast: #FFFFFF;

  /* Semantic Feedback */
  --success: #087443;
  --success-bg: #EAF8F0;
  --success-border: #B7E7CE;

  --warning: #A15C00;
  --warning-bg: #FFF5E5;
  --warning-border: #FCD8A2;

  --danger: #B42318;
  --danger-bg: #FEF0EF;
  --danger-border: #FECDCA;

  --info: #175CD3;
  --info-bg: #EEF4FF;
  --info-border: #C8DCFF;

  /* Metrics & Spacing */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Elevation */
  --shadow-sm: 0 1px 2px rgba(16, 24, 40, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(16, 24, 40, 0.08), 0 2px 4px -2px rgba(16, 24, 40, 0.04);
}
```

---

## 3. Application Shell Structure

```text
+-----------------------------------------------------------------------------------------------+
| AppHeader: [ProductIQ AI] [Global Search] [Env: Local | Backend: OK | DB: OK | Ollama: OK]   |
+-------------------+---------------------------------------------------------------------------+
| AppSidebar        | Main Workspace                                                            |
|                   |                                                                           |
| Overview          | Top Sub-header / Breadcrumbs & Workspace Controls                         |
| Product Analyzer  | +-----------------------------------------------------------------------+ |
| Catalog Engine    | | Work Area / Data Tables / Drawers / Visualizations                    | |
| Review Center     | |                                                                       | |
| Data Quality      | |                                                                       | |
| Evaluation        | |                                                                       | |
| AI Governance     | |                                                                       | |
| Global Search     | |                                                                       | |
|                   | +-----------------------------------------------------------------------+ |
| System Health     |                                                                           |
| Audit Log         |                                                                           |
| Settings          |                                                                           |
+-------------------+---------------------------------------------------------------------------+
| AppStatusBar: Latency: 4ms | Storage: SQLite | Model: llama3.2:3b | Active Job: IDLE          |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Key Workspaces & Modules

1. **Executive Overview (`Overview.jsx`)**: System-wide product metrics, commerce readiness distribution, review backlog, quality score averages, and recent ingestion activities.
2. **Product Analyzer (`ProductAnalyzer.jsx`)**: Source workspace (Files, URLs, Raw Text), deterministic extraction stages, technical data tables, and side-drawer attribute intelligence.
3. **Catalog Engine (`CatalogEngine.jsx`)**: Bulk CSV/XLSX catalog batch processing, product inspector modal, filtering, and export.
4. **Review Center (`ReviewCenter.jsx`)**: Dense operational triage queue, side-by-side discrepancy resolver, 6 resolution actions, and immutable audit trails.
5. **Data Quality Center (`DataQuality.jsx`)**: Systemic quality defect breakdown (missing required fields, ungrounded attributes, invalid units, confidence penalties).
6. **Trust Report (`TrustReport.jsx`)**: Deterministic explainability for commerce readiness qualification.
7. **AI Governance & Registries (`AIGovernance.jsx`)**: Model registry, prompt version tracking, pipeline reproducibility, and evaluation benchmarks.
8. **Evaluation Dashboard (`EvaluationDashboard.jsx`)**: 10-product gold standard benchmark suite, precision/recall/F1 metrics, calibration bins, confusion matrices, and regression detection.
9. **Global Product Search (`ProductSearch.jsx`)**: Multi-attribute filtering across stored catalog records.
10. **System Health (`SystemHealth.jsx`)**: Real-time component telemetry, database metrics, and Ollama runtime status.
11. **Audit Log (`AuditLog.jsx`)**: Immutable provenance and resolution action history.
