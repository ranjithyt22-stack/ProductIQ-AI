"""
Excel Source Adapter for ingesting Excel spreadsheets (.xlsx, .xls) using pandas & openpyxl.
"""

import os
import uuid
import pandas as pd
from pathlib import Path
from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


class ExcelSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting Excel files."""

    def ingest(self, file_path: str) -> SourceDocument:
        if not file_path or not os.path.exists(file_path):
            raise IngestionError("Excel file does not exist on disk.")

        filename = Path(file_path).name
        source_id = f"excel_{uuid.uuid4().hex[:12]}"

        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            if not sheet_names:
                raise IngestionError("Excel file contains no worksheets.")

            all_sheet_rows = []
            for sheet in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet, dtype=str)
                df = df.fillna("").map(lambda x: x.strip() if isinstance(x, str) else x)
                if df.empty:
                    continue

                sheet_lines = [f"--- SHEET: {sheet} ---"]
                for idx, row in df.iterrows():
                    row_items = [f"{col}: {row[col]}" for col in df.columns if row[col]]
                    if row_items:
                        sheet_lines.append(f"ROW {idx + 1}: " + " | ".join(row_items))

                if len(sheet_lines) > 1:
                    all_sheet_rows.extend(sheet_lines)

            excel_file.close()

        except IngestionError:
            raise
        except Exception as e:
            raise IngestionError(f"Failed to parse Excel file: {str(e)}") from e

        if not all_sheet_rows:
            raise IngestionError("Excel file contains no usable data records across sheets.")

        full_content = f"EXCEL SPREADSHEET: {filename}\nSHEETS: {', '.join(sheet_names)}\n\n" + "\n".join(all_sheet_rows)

        return SourceDocument(
            source_id=source_id,
            source_type="excel",
            source_name=filename,
            content=full_content,
            local_path=file_path,
            metadata={
                "sheet_names": sheet_names
            },
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
