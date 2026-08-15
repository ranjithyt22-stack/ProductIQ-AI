"""
Extraction Engine for ProductIQ AI.
Handles PDF text extraction via PyMuPDF (fitz) and structured AI parsing via Ollama local API.
"""

import os
import json
import re
import requests
import pymupdf as fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple, Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def deterministic_source_extraction(document_text: str) -> Dict[str, Any]:
    """Conservative local fallback: only maps labelled source lines, never infers facts."""
    product = {"product_name": None, "manufacturer": None, "product_code": None, "category": None, "description": None}
    specs = []
    aliases = {"product name": "product_name", "manufacturer": "manufacturer", "product code": "product_code", "part number": "product_code", "category": "category", "description": "description"}
    page = 1
    for line in document_text.splitlines():
        marker = re.match(r"\s*---\s*PAGE\s+(\d+)\s*---", line, re.I)
        if marker:
            page = int(marker.group(1)); continue
        match = re.match(r"\s*(?:[-*]\s*)?([^:]{2,80}):\s*(.+?)\s*$", line)
        if not match: continue
        label, value = match.group(1).strip(), match.group(2).strip()
        key = aliases.get(label.lower())
        if key:
            product[key] = value
            continue
        if label.lower() in {"technical specifications", "recommended industrial applications", "compliance & certifications"}: continue
        number = re.match(r"^(.+?)\s+([a-zA-Z°µ/]+)$", value)
        specs.append({"name": label, "value": number.group(1) if number else value, "unit": number.group(2) if number else None, "page": page, "evidence": line})
    return {"product": product, "specifications": specs, "applications": [], "keywords": [], "enrichment": {}}


def extract_pdf_pages(pdf_path: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Extracts text page by page from PDF using PyMuPDF.
    Returns: (list of page dicts, error_message if any)
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return [], "PDF file not found."

    filename = os.path.basename(pdf_path)
    page_records = []

    try:
        doc = fitz.open(pdf_path)

        for page_idx, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            if text.strip():
                page_records.append({
                    "source_id": f"source_{page_idx:03d}",
                    "filename": filename,
                    "page": page_idx,
                    "text": text.strip()
                })

        doc.close()

        if not page_records:
            return [], "Text extraction failed. OCR may be required."

        return page_records, ""

    except Exception as e:
        return [], f"PDF extraction error: {str(e)}"


def call_ollama_structured_extraction(
    document_text: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Calls local Ollama (llama3.2:3b) to perform structured JSON extraction.
    Strictly instructs LLM against hallucinating specifications.
    """
    context_str = ""
    if user_context:
        ctx_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in user_context.items() if v]
        if ctx_parts:
            context_str = "USER-PROVIDED PRODUCT METADATA HINTS:\n" + "\n".join(ctx_parts) + "\n\n"

    prompt = f"""
You are ProductIQ AI, an enterprise AI assistant for industrial product intelligence.

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION RULES:
1. Extract ONLY facts explicitly supported by the provided document text or input details.
2. NEVER invent, guess, or hallucinate technical specifications.
3. If a field or attribute is NOT mentioned in the text (for example "Warranty Period" or "Weight"), use null. Do NOT invent values like "1 year".
4. Preserve original units.
5. Separate numeric values from units (e.g. value: "50", unit: "mm"). Do NOT include unit in value string.
6. "applications" and "keywords" MUST be flat arrays of strings (e.g., ["Industrial automation", "Assembly machines"]).
7. Return ONLY a single valid JSON object. Do not include markdown code block syntax outside JSON or explanatory text.

{context_str}SOURCE DOCUMENT TEXT:
{document_text[:12000]}

REQUIRED JSON STRUCTURE:
{{
  "product": {{
    "product_name": null,
    "manufacturer": null,
    "product_code": null,
    "category": null,
    "description": null
  }},
  "specifications": [
    {{
      "name": "Attribute Name",
      "value": "Value String",
      "unit": "Unit String or null",
      "page": 1,
      "evidence": "Exact text sentence from document"
    }}
  ],
  "applications": [
    "Application 1",
    "Application 2"
  ],
  "keywords": [
    "Keyword 1",
    "Keyword 2"
  ],
  "enrichment": {{
    "search_terms": ["Term 1"],
    "category_path": ["Industrial Equipment"],
    "suggested_applications": ["App 1"]
  }}
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=(2.0, 10.0)
        )
        response.raise_for_status()

        result = response.json()
        raw_text = result.get("response", "").strip()

        # Clean JSON markdown fences if LLM accidentally adds them
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        parsed_data = json.loads(raw_text)
        return parsed_data, ""

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException):
        fallback = deterministic_source_extraction(document_text)
        if fallback["specifications"] or any(fallback["product"].values()):
            return fallback, ""
        return None, "Cannot connect to local Ollama server at http://localhost:11434. Please ensure Ollama is running."
    except json.JSONDecodeError as e:
        return None, f"AI returned invalid JSON syntax: {str(e)}"
    except Exception as e:
        return None, f"Ollama API call error: {str(e)}"

