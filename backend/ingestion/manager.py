"""
Master Source Ingestion Manager & Adapter Orchestrator for ProductIQ AI.
Integrates file upload validation, persistent saving, multi-adapter ingestion,
and multi-source document bundling with provenance preservation.
"""

import os
import uuid
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union


from backend.config import MAX_FILE_SIZE, UPLOADS_DIR
from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument
from backend.ingestion.pdf import PDFSourceAdapter
from backend.ingestion.web import WebSourceAdapter, validate_public_url
from backend.ingestion.csv import CSVSourceAdapter
from backend.ingestion.excel import ExcelSourceAdapter
from backend.ingestion.docx import DocxSourceAdapter
from backend.ingestion.text import TextSourceAdapter
from backend.ingestion.image import ImageSourceAdapter

ALLOWED_EXTENSIONS = {
    ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".txt", ".md", ".png", ".jpg", ".jpeg"
}

# Registry mapping extensions to adapter instances
ADAPTER_MAP = {
    ".pdf": PDFSourceAdapter(),
    ".csv": CSVSourceAdapter(),
    ".xlsx": ExcelSourceAdapter(),
    ".xls": ExcelSourceAdapter(),
    ".docx": DocxSourceAdapter(),
    ".txt": TextSourceAdapter(),
    ".md": TextSourceAdapter(),
    ".png": ImageSourceAdapter(),
    ".jpg": ImageSourceAdapter(),
    ".jpeg": ImageSourceAdapter(),
}


def save_upload(file_path_or_obj: Union[str, Any]) -> str:
    """
    Validates uploaded file size and extension, copying it into persistent uploads/ storage.
    Prevents path traversal and returns absolute/safe persistent file path.
    """
    if not file_path_or_obj:
        raise IngestionError("No uploaded file provided.")

    path_str = file_path_or_obj if isinstance(file_path_or_obj, str) else getattr(file_path_or_obj, "name", str(file_path_or_obj))

    if not path_str or not os.path.isfile(path_str):
        raise IngestionError("Uploaded file does not exist on disk.")

    size = os.path.getsize(path_str)
    if size == 0:
        raise IngestionError("Uploaded file is empty.")

    if size > MAX_FILE_SIZE:
        raise IngestionError(f"File exceeds the maximum size limit ({MAX_FILE_SIZE // 1024 // 1024} MB).")

    ext = Path(path_str).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise IngestionError(f"Unsupported file format '{ext or 'unknown'}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    raw_name = Path(path_str).name
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in raw_name)
    destination = os.path.join(UPLOADS_DIR, f"{uuid.uuid4().hex[:12]}_{safe_name}")

    with open(path_str, "rb") as src, open(destination, "wb") as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)

    return destination


def ingest_file(file_path: str) -> SourceDocument:
    """Ingests a single local file using appropriate adapter."""
    if not file_path or not os.path.exists(file_path):
        raise IngestionError(f"File path '{file_path}' does not exist.")

    ext = Path(file_path).suffix.lower()
    adapter = ADAPTER_MAP.get(ext)
    if not adapter:
        raise IngestionError(f"No ingestion adapter available for file extension '{ext}'.")

    return adapter.ingest(file_path)


def ingest_url(url: str) -> SourceDocument:
    """Ingests a public website URL using WebSourceAdapter."""
    adapter = WebSourceAdapter()
    return adapter.ingest(url)


def ingest_text(raw_text: str, source_name: str = "Pasted Product Text") -> SourceDocument:
    """Ingests plain pasted product text or supplementary specifications."""
    clean_text = (raw_text or "").strip()
    if not clean_text:
        raise IngestionError("Pasted text is empty.")

    source_id = f"text_{uuid.uuid4().hex[:12]}"
    return SourceDocument(
        source_id=source_id,
        source_type="pasted_text",
        source_name=source_name,
        content=clean_text,
        metadata={"length": len(clean_text)},
        mime_type="text/plain"
    )


def ingest_sources(
    files: Optional[Iterable[str]] = None,
    urls: Optional[Iterable[str]] = None,
    text: Optional[str] = None
) -> List[SourceDocument]:
    """
    Master ingestion entry point supporting multi-source combinations.
    Combines files, URLs, and pasted text into a list of normalized SourceDocument instances.
    """
    documents: List[SourceDocument] = []
    errors: List[str] = []

    for f_path in (files or []):
        if not f_path:
            continue
        try:
            doc = ingest_file(f_path)
            documents.append(doc)
        except IngestionError as e:
            errors.append(f"File '{Path(f_path).name}': {str(e)}")

    for u_str in (urls or []):
        u_clean = (u_str or "").strip()
        if not u_clean:
            continue
        try:
            doc = ingest_url(u_clean)
            documents.append(doc)
        except IngestionError as e:
            errors.append(f"URL '{u_clean}': {str(e)}")

    if (text or "").strip():
        try:
            doc = ingest_text(text.strip())
            documents.append(doc)
        except IngestionError as e:
            errors.append(f"Pasted text: {str(e)}")

    if not documents:
        if errors:
            raise IngestionError("Source ingestion failed:\n" + "\n".join(errors))
        raise IngestionError("Please provide at least one valid source file, URL, or text description.")

    return documents
