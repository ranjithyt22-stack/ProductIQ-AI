# Deployment Guide

## Local Zero-Cost Execution (Primary Hackathon Target)
ProductIQ AI runs 100% locally with zero subscription costs or paid API keys.

### System Requirements:
- Python 3.10+
- Ollama local inference service (`llama3.2:3b`)

### Running Locally:
1. Start Ollama service:
   ```bash
   ollama run llama3.2:3b
   ```
2. Launch Gradio Web Application:
   ```powershell
   .venv\Scripts\python.exe app.py
   ```
   Access web interface at: `http://127.0.0.1:7860`

3. Launch FastAPI REST API Server:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
   ```
   Access OpenAPI docs at: `http://127.0.0.1:8000/docs`

## Environment Configuration Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL of local Ollama inference service |
| `OLLAMA_MODEL` | `llama3.2:3b` | Local LLM model tag |
| `API_HOST` | `0.0.0.0` | FastAPI server host bind address |
| `API_PORT` | `8000` | FastAPI server port |
| `UPLOADS_DIR` | `uploads` | Persistent directory for uploads and exports |
| `MAX_FILE_SIZE` | `26214400` (25 MB) | Maximum upload file size in bytes |
| `URL_TIMEOUT` | `12.0` | Maximum web scraping request timeout in seconds |
| `MAX_WEB_CONTENT_SIZE` | `2097152` (2 MB) | Maximum web page HTML content size |
