# Kinza Commercial Intelligence MVP

A deterministic Streamlit demo that presents commercial value first and keeps the data-platform layer replaceable.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app generates its data in memory, so there is no setup job or database required.

## Validate the planted stories

```powershell
python validate_stories.py
```

Expected outcomes:

- Jeddah Cola 330ml sales decline is supply-driven.
- Current stock is 4,500 units and seven-day demand is 13,000 units.
- The predicted shortage and transfer recommendation are 8,500 units.
- Riyadh remains above safety stock after the transfer.
- Protected sales are approximately SAR 184k.
- One promotion damages margin and one distributor is visibly deteriorating.

## Project shape

- `app.py` — four-screen Streamlit product.
- `data_model.py` — deterministic synthetic source and presentation datasets.
- `business_logic.py` — reusable calculations and constrained business Q&A.
- `validate_stories.py` — executable checks for the demo narrative.
- `sql/` — Databricks-ready table/view definitions for the inventory story.
- `app.yaml` — minimal Databricks Apps command.

## Databricks migration path

1. Materialize the eight source datasets from `data_model.py` as Unity Catalog Delta tables.
2. Build the Gold views in `sql/` and extend the same pattern for executive, sales, distributor, and promotion views.
3. Replace calls to `build_demo_data()` with SQL Warehouse queries.
4. Attach the SQL Warehouse as a Databricks App resource and grant the app service principal `USE CATALOG`, `USE SCHEMA`, `SELECT`, and warehouse `CAN USE` permissions.
5. Keep the constrained Q&A until the curated Gold metrics are stable; then add Genie over Gold tables only.

