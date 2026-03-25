# Healthcare Enterprise Data Trust Workbench

A static Streamlit PoC designed to demonstrate three pain points in a healthcare provider environment:

1. **Clinical data trust** — competing KPI definitions and no single source of truth.
2. **EMR integration reliability** — late / failed interfaces and incident visibility.
3. **Analytics adoption** — trusted KPIs and measurable manual work reduction.

## What is included

- `app.py` — Streamlit app
- `data/healthcare_data_trust_poc_data.xlsx` — static sample workbook
- `scripts/bootstrap_postgres.py` — loads workbook tables into Postgres
- `scripts/create_static_data.py` — confirms where the packaged static data lives
- `notebooks/01_data_setup.ipynb` — lightweight notebook walkthrough
- `healthcare_enterprise_data_trust_poc/` — shared config and database logic

## Railway database setup

This app is designed to use Railway Postgres through the `DATABASE_URL` environment variable.

The local fallback in `db.py` exists only for development, but your intended deployment is Railway.

## Quick start

```bash
pip install -r requirements.txt
python scripts/bootstrap_postgres.py
streamlit run app.py
```

## What the app shows

### 1) Problem / Before State
A deliberately conflicting KPI submission table where Finance, Clinical Operations, and Revenue Cycle report different values for the same KPI.

### 2) Governance & Certification
A KPI registry that shows owner, steward, definition, source object, consumer group, and certification status.

### 3) Integration & Lineage
EMR / claims interface health, incidents, and a simple lineage graph from source systems to certified executive KPIs.

### 4) Data Quality
Rule results with intentional issues:
- one missing March budget value
- one failed lab interface
- one delayed claims feed
- one KPI with no owner

### 5) Executive View
A trusted pipeline that merges actual patient revenue and budget, calculates variance, and exports a certified summary.

### 6) Adoption & Value
Static monthly adoption metrics to show business value, not just technical delivery.

## Default desktop exports

When the app runs locally on the intended Windows machine, the executive summary export defaults to:

- `C:\Users\<your-user>\OneDrive\Desktop\certified_clinical_summary.xlsx`
- `C:\Users\<your-user>\OneDrive\Desktop\certified_clinical_summary.csv`

If that path does not exist, the app falls back to a local `desktop_exports` folder.
