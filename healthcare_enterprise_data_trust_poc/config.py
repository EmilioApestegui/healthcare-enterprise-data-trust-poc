from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CSV_DIR = DATA_DIR / "csv"
WORKBOOK_PATH = DATA_DIR / "healthcare_data_trust_poc_data.xlsx"
TARGET_DB = "healthcare_enterprise_data_trust_poc"

def export_paths() -> dict:
    desktop = Path.home() / "OneDrive" / "Desktop"
    if not desktop.exists():
        desktop = PROJECT_ROOT / "desktop_exports"
        desktop.mkdir(parents=True, exist_ok=True)

    return {
        "xlsx": desktop / "certified_clinical_summary.xlsx",
        "csv": desktop / "certified_clinical_summary.csv",
    }
