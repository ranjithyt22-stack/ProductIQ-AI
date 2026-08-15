"""
Text Source Adapter for ingesting plain text (.txt) and Markdown (.md) product specifications.
"""

import os
import uuid
from pathlib import Path

from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


class TextSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting TXT and Markdown files."""

    def ingest(self, file_path: str) -> SourceDocument:
        if not file_path or not os.path.exists(file_path):
            raise IngestionError("Text file does not exist on disk.")

        filename = Path(file_path).name
        ext = Path(file_path).suffix.lower()
        source_id = f"text_{uuid.uuid4().hex[:12]}"

        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="replace").strip()
        except Exception as e:
            raise IngestionError(f"Failed to read text file: {str(e)}") from e

        if not content:
            raise IngestionError("Text file is empty.")

        source_type = "markdown" if ext == ".md" else "text"
        mime_type = "text/markdown" if ext == ".md" else "text/plain"

        return SourceDocument(
            source_id=source_id,
            source_type=source_type,
            source_name=filename,
            content=content,
            local_path=file_path,
            metadata={"character_count": len(content)},
            mime_type=mime_type
        )
