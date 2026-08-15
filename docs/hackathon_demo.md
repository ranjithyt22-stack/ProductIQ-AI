# Hackathon Demonstration Guide (3-Minute Flow)

Follow this step-by-step procedure to showcase all key hackathon judging features in under 3 minutes.

## Demo Preparation
1. Ensure Python dependencies are installed and Ollama service is running.
2. Launch Gradio application: `.venv\Scripts\python.exe app.py`.
3. Open browser to `http://127.0.0.1:7860`.

---

## 3-Minute Demo Flow

### Step 1: Zero-Cost Application Startup (15 Seconds)
- Point out that the app started instantly without polling or loading sample data.
- Show that no OpenAI, Gemini, or Anthropic API keys are configured (100% Zero-Cost Local AI).

### Step 2: Single Product Analysis (45 Seconds)
- Click **"Load Sample Pneumatic Cylinder Datasheet"** or upload `data/Test_Temperature_Sensor.pdf`.
- Click **"Analyze Single Product with AI"**.
- Point out:
  1. **Product Quality Readiness Score** (e.g. 95/100, `READY FOR COMMERCE`).
  2. **Product Overview & AI Enrichment**: Highlighting clear distinction between **Source Facts** and **AI-Generated Taxonomy/Keywords**.
  3. **Technical Specifications Table**: Clean attribute, value, unit, and confidence.

### Step 3: Evidence Traceability & Anti-Hallucination (30 Seconds)
- Switch to **"Evidence & Traceability"** tab.
- Select `Operating Pressure` or `Bore Diameter` from the dropdown.
- Show verbatim quote snippet and page number matching. Explain how ProductIQ AI eliminates hallucinations by tracing attributes to exact source text.

### Step 4: Deterministic Validation & Human Review (30 Seconds)
- Switch to **"Validation & Consistency"** tab to highlight 8-category rule results.
- Switch to **"Human Review & Verification"** tab.
- Change an attribute value (e.g., set `Operating Temperature` value to `2.0`, unit `°C`).
- Click **"Confirm & Mark Human Verified"** and point out how the status updates to `HUMAN VERIFIED`.

### Step 5: Commerce Exports & Catalog Engine (40 Seconds)
- Show **"Export & Raw Data"** tab (Download JSON / CSV).
- Switch to **"Catalog Engine"** tab.
- Click **"Load Sample Industrial Catalog"** and **"Analyze Catalog Batch"**.
- Demonstrate aggregate metrics, readiness summary cards, fault isolation, search/filtering, and detailed catalog item inspector.
