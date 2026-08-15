"""
Configuration settings for ProductIQ AI.
Reads environment variables with safe default fallbacks.
"""

import os

# Ollama Local LLM Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# REST API Server Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Directories
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
DATA_DIR = os.getenv("DATA_DIR", "data")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(25 * 1024 * 1024)))
URL_TIMEOUT = float(os.getenv("URL_TIMEOUT", "12"))
MAX_WEB_CONTENT_SIZE = int(os.getenv("MAX_WEB_CONTENT_SIZE", str(2 * 1024 * 1024)))

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
