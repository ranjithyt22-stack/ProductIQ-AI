# ProductIQ AI REST API Reference

ProductIQ AI provides enterprise REST API endpoints built with FastAPI and documented via OpenAPI (`http://localhost:8000/docs`).

## Available Endpoints

### 1. Health & Liveness
- **`GET /health`**
  - **Response**: `{"status": "ok", "ollama": "available", "model": "llama3.2:3b"}`

### 2. Product Intelligence Analysis
- **`POST /analyze`** (Form-Data / Files)
  - Accepts metadata fields and/or uploaded PDF file.
- **`POST /analyze/url`** (JSON)
  - Accepts `{"url": "https://example.com/product", "manufacturer": "Acme"}`.
- **`POST /analyze/file`** (Form-Data)
  - Accepts uploaded file (`PDF`, `DOCX`, `CSV`, `Excel`, `TXT`).
- **`POST /analyze/text`** (JSON)
  - Accepts `{"text": "Pneumatic cylinder bore 50 mm..."}`.
- **`POST /analyze/multi-source`** (Form-Data)
  - Accepts combined files, URLs string, and supplementary text.

### 3. Standalone Engines
- **`POST /validate`** (JSON)
  - Accepts product metadata and specifications list; returns 8-category validation check results.
- **`POST /enrich`** (JSON)
  - Accepts product data; returns taxonomy path, search terms, and suggested industrial applications.

### 4. Catalog Engine & Lookups
- **`POST /catalog/analyze`** (Multipart File Upload)
  - Accepts catalog CSV; returns batch catalog processing results with fault isolation.
- **`GET /catalog/{catalog_id}`** (Path Parameter)
  - Retrieves catalog batch result by ID.
- **`GET /product/{product_id}`** (Path Parameter)
  - Retrieves single product intelligence record by Product ID.

## HTTP Status Codes & Error Handling
- `200 OK`: Successful operation.
- `400 Bad Request`: Validation error or unreadable source file.
- `404 Not Found`: Product ID or Catalog ID does not exist.
- `422 Unprocessable Entity`: Invalid request JSON body schema.
- `500 Internal Server Error`: Technical server error (stack trace sanitized).
