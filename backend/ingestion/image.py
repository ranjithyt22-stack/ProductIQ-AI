"""
Image Source Adapter for ingesting product photos and specification screenshots with local OCR fallback.
"""

import os
import uuid
from pathlib import Path

from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


class ImageSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting image files with OCR fallback handling."""

    def ingest(self, file_path: str) -> SourceDocument:
        if not file_path or not os.path.exists(file_path):
            raise IngestionError("Image file does not exist on disk.")

        filename = Path(file_path).name
        ext = Path(file_path).suffix.lower()
        source_id = f"img_{uuid.uuid4().hex[:12]}"

        ocr_text = ""
        ocr_engine = None

        # Attempt optional local pytesseract OCR if installed
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(file_path)
            ocr_text = pytesseract.image_to_string(img).strip()
            ocr_engine = "pytesseract"
        except ImportError:
            ocr_text = ""
        except Exception as e:
            ocr_text = ""

        if not ocr_text:
            raise IngestionError(
                "Image OCR module (pytesseract/tesseract-ocr) is not installed on system. "
                "Please upload a PDF, DOCX, CSV, Excel, TXT, or URL source instead."
            )

        mime_type = f"image/{ext.lstrip('.')}"
        full_content = f"IMAGE SOURCE (OCR via {ocr_engine}): {filename}\n\n{ocr_text}"

        return SourceDocument(
            source_id=source_id,
            source_type="image",
            source_name=filename,
            content=full_content,
            local_path=file_path,
            metadata={"ocr_engine": ocr_engine},
            mime_type=mime_type
        )
