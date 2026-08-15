"""
ProductIQ AI Ingestion Module.
"""

from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument
from backend.ingestion.pdf import PDFSourceAdapter
from backend.ingestion.web import WebSourceAdapter, validate_public_url
from backend.ingestion.csv import CSVSourceAdapter
from backend.ingestion.excel import ExcelSourceAdapter
from backend.ingestion.docx import DocxSourceAdapter
from backend.ingestion.text import TextSourceAdapter
from backend.ingestion.image import ImageSourceAdapter
from backend.ingestion.manager import (
    save_upload, ingest_file, ingest_url, ingest_text, ingest_sources
)

__all__ = [
    "BaseSourceAdapter",
    "IngestionError",
    "SourceDocument",
    "PDFSourceAdapter",
    "WebSourceAdapter",
    "validate_public_url",
    "CSVSourceAdapter",
    "ExcelSourceAdapter",
    "DocxSourceAdapter",
    "TextSourceAdapter",
    "ImageSourceAdapter",
    "save_upload",
    "ingest_file",
    "ingest_url",
    "ingest_text",
    "ingest_sources"
]
