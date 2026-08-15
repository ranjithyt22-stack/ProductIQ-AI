"""
PDF Source Adapter using PyMuPDF (fitz) for page-by-page extraction and page metadata tracking.
"""

import os
import uuid
import pymupdf as fitz
from pathlib import Path
from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


class PDFSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting PDF datasheets and documents."""

    def ingest(self, file_path: str) -> SourceDocument:
        if not file_path or not os.path.exists(file_path):
            raise IngestionError("PDF file does not exist on disk.")

        filename = Path(file_path).name
        source_id = f"pdf_{uuid.uuid4().hex[:12]}"

        pages = []
        try:
            doc = fitz.open(file_path)
            doc_metadata = doc.metadata or {}

            for page_idx, page in enumerate(doc, start=1):
                page_text = (page.get_text("text") or "").strip()
                if page_text:
                    pages.append({
                        "source_id": source_id,
                        "filename": filename,
                        "page": page_idx,
                        "text": page_text
                    })

            doc.close()
        except Exception as e:
            raise IngestionError(f"Unable to parse PDF document: {str(e)}") from e

        full_text = "\n\n".join(f"--- PAGE {p['page']} ---\n{p['text']}" for p in pages if p["text"])
        if not full_text:
            raise IngestionError("PDF contains no extractable text. Scanned PDFs may require OCR.")

        return SourceDocument(
            source_id=source_id,
            source_type="pdf",
            source_name=filename,
            content=full_text,
            local_path=file_path,
            pages=pages,
            metadata={
                "page_count": len(pages),
                "author": doc_metadata.get("author", ""),
                "title": doc_metadata.get("title", ""),
                "subject": doc_metadata.get("subject", "")
            },
            mime_type="application/pdf"
        )
