from __future__ import annotations

from .config import WORKBOOK_PATH, CSV_DIR

def describe_assets() -> dict:
    return {
        "workbook": str(WORKBOOK_PATH),
        "csv_dir": str(CSV_DIR),
    }
