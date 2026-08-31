# Kinza Commercial Intelligence — Databricks-backed MVP

A deterministic executive decision-intelligence demo with a Databricks lakehouse,
Unity Catalog governance assets, Genie grounding instructions, and a Streamlit
presentation layer. It runs locally without credentials and can connect to a
Databricks SQL warehouse when configured.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Without Databricks credentials, the app clearly labels itself as using the local
deterministic dataset. Never enter a token into the application UI.

## Build the Databricks layer (Free Edition)

### Automated deployment (recommended)

After configuring `.streamlit/secrets.toml`, run:

```powershell
.venv\Scripts\python.exe deploy_to_databricks.py
```

This idempotent command creates and loads all eight Bronze tables, rebuilds the
Silver/Gold layer, applies supported governance metadata, and verifies the
8,500-unit transfer and SAR 184,000 protected-revenue result.

### Workspace notebook option

1. In the Databricks workspace, create a notebook and paste/import
   `databricks_assets/00_setup_and_generate.py`.
2. Attach serverless compute and run all cells. It creates the eight requested
   Bronze Delta tables in `workspace.kinza_commercial`.
3. Run `databricks_assets/01_silver_gold.sql` in SQL Editor or a SQL notebook.
4. Run `databricks_assets/02_governance.sql` to add owners, definitions, certification
   properties, and governance metadata.
5. Open **SQL Warehouses**, start the available warehouse, and copy its server
   hostname and HTTP path from the connection details.
6. For local development, copy `.streamlit/secrets.toml.example` to
   `.streamlit/secrets.toml` and supply the three settings. The real secrets file
   is gitignored.
7. Configure a Genie Agent using `databricks_assets/genie_instructions.md`; expose only
   the curated assets listed there.

Free Edition is quota-limited and intended for learning/prototyping rather than
commercial production. Databricks Apps can stop after 24 hours and be restarted.

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

- `app.py` — six-screen executive product, including Action Center and Data Trust.
- `data_model.py` — deterministic synthetic source and presentation datasets.
- `business_logic.py` — reusable calculations and constrained business Q&A.
- `db.py` — Databricks SQL connector with explicit local fallback.
- `deploy_to_databricks.py` — repeatable end-to-end warehouse deployment.
- `validate_stories.py` — executable checks for the demo narrative.
- `databricks_assets/` — source generation, Silver/Gold SQL, governance, and Genie setup.
- `sql/` — compact standalone SQL examples retained for reference.
- `app.yaml` — minimal Databricks Apps command.

## Customer demonstration sequence

1. Executive Overview: identify the Jeddah decline.
2. Ask Your Business: establish that demand is healthy and supply is constrained.
3. Inventory Intelligence: show the forecast, shortage, source excess, transfer,
   and protected revenue.
4. Action Center: turn the insight into an owned, prioritized decision.
5. Sales & Distribution: reveal the margin-dilutive promotion and distributor risk.
6. Data Trust: reveal definitions and lineage in the app, then open Unity Catalog
   to prove ownership, permissions, descriptions, and captured lineage.

See `docs/DEMO_RUNBOOK.md` for the presenter script.
