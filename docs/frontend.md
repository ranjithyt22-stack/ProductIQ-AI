# ProductIQ AI - Frontend Architecture Documentation

## 1. Overview
The ProductIQ AI frontend is a single-page application built using React 18 and Vite. It interfaces with the FastAPI backend through a typed, centralized REST client (`frontend/src/services/api.js`).

## 2. Component Architecture
```
frontend/src/
├── App.jsx                     # Root application shell with tab routing
├── index.css                   # Global Dark Navy industrial theme variables
├── main.jsx                    # Application entry point
├── components/
│   ├── AppHeader.jsx           # Global header with live Backend & Ollama health badges
│   ├── CommerceReadyPanel.jsx  # Commerce syndication payload preview
│   ├── CompletenessPanel.jsx   # Data completeness & schema validation audit
│   ├── EmptyState.jsx          # Professional zero-data state with demo loader
│   ├── EnrichmentPanel.jsx     # AI taxonomy, category path & search keywords
│   ├── ErrorState.jsx          # Human-readable error display with retry action
│   ├── EvidencePanel.jsx       # Verbatim source quote & page traceability inspector
│   ├── ExportPanel.jsx         # JSON and CSV export handlers
│   ├── FileUploader.jsx        # Multi-format document upload dropzone
│   ├── HumanReview.jsx         # Human-in-the-loop attribute override workflow
│   ├── LoadingState.jsx        # Localized loading spinner with stage description
│   ├── ProcessingPipeline.jsx  # 10-stage visible intelligence pipeline indicator
│   ├── ProductInspector.jsx    # Tabbed deep-dive catalog inspector
│   ├── ProductOverview.jsx     # Source-backed vs AI-enriched metadata display
│   ├── QualityScore.jsx        # 5-dimension quality breakdown badge
│   ├── SourceComparison.jsx    # Multi-source conflict and provenance analyzer
│   ├── SourceList.jsx          # Active source chips with removal actions
│   ├── Specifications.jsx      # Normalized technical parameters table
│   ├── StatusBadge.jsx         # Semantic status indicators (PASS, WARNING, etc.)
│   ├── TextInput.jsx           # Supplementary specification text input
│   └── UrlInput.jsx            # Webpage URL input with protocol validation
└── pages/
    ├── ProductAnalyzer.jsx     # Single Product Intelligence workspace
    └── CatalogEngine.jsx       # Scalable Batch Catalog Ingestion workspace
```

## 3. State Management & Zero-Flicker Guarantees
- **Atomic Analysis State**: `ProductAnalyzer.jsx` maintains an atomic `{ loading, error, record }` state object. Whenever input sources change, the previous analysis is wiped cleanly without remounting the entire component tree.
- **Independent Tab State**: Switching between the Single Product Analyzer and Catalog Engine does not destroy or reset in-progress sessions.
- **Double-Click Protection**: Analysis triggers utilize `useRef` locks (`analyzingRef`) to prevent duplicate HTTP requests.

## 4. UI Style Guide & Tokens
- **Background Primary**: `#0B0F19` (Deep Navy)
- **Card Background**: `#0F172A` (Dark Slate Navy)
- **Card Secondary**: `#1E293B`
- **Border**: `#1E293B` / `#334155`
- **Accent Primary**: `#2563EB` (Industrial Blue)
- **Success**: `#22C55E` / `#34D399`
- **Warning**: `#F59E0B` / `#FBBF24`
- **Danger**: `#EF4444` / `#F87171`
- **Icons**: Lucide React SVG icons (Zero Emojis).
