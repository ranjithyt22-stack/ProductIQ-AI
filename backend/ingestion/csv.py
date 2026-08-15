"""
CSV Source Adapter for ingesting CSV product catalogs and unstructured tabular data.
"""

import os
import uuid
import pandas as pd
from pathlib import Path
from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


class CSVSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting CSV product catalogs."""

    def ingest(self, file_path: str) -> SourceDocument:
        if not file_path or not os.path.exists(file_path):
            raise IngestionError("CSV file does not exist on disk.")

        filename = Path(file_path).name
        source_id = f"csv_{uuid.uuid4().hex[:12]}"

        try:
            df = pd.read_csv(file_path, dtype=str, encoding_errors="replace")
        except Exception as e:
            raise IngestionError(f"Failed to parse CSV file: {str(e)}") from e

        df = df.fillna("").map(lambda x: x.strip() if isinstance(x, str) else x)
        if df.empty:
            raise IngestionError("CSV file is empty or contains no valid rows.")

        content_rows = []
        for idx, row in df.iterrows():
            row_items = [f"{col}: {row[col]}" for col in df.columns if row[col]]
            if row_items:
                content_rows.append(f"ROW {idx + 1}: " + " | ".join(row_items))

        if not content_rows:
            raise IngestionError("CSV contains no non-empty values.")

        full_content = f"CSV CATALOG: {filename}\nTOTAL ROWS: {len(df)}\nCOLUMNS: {', '.join(df.columns)}\n\n" + "\n".join(content_rows)

        return SourceDocument(
            source_id=source_id,
            source_type="csv",
            source_name=filename,
            content=full_content,
            local_path=file_path,
            metadata={
                "row_count": len(df),
                "columns": list(df.columns)
            },
            mime_type="text/csv"
        )
