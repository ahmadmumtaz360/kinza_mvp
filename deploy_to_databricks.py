"""Deploy the deterministic Kinza dataset and governed lakehouse through SQL Warehouse.

Run with: .venv/Scripts/python deploy_to_databricks.py
The local secrets file is read but credentials are never printed.
"""

from __future__ import annotations

from pathlib import Path
import tomllib
from datetime import date

import pandas as pd
from databricks import sql

from data_model import build_demo_data


ROOT = Path(__file__).resolve().parent
CATALOG = "workspace"
SCHEMA = "kinza_commercial"


DDL = {
    "bronze_products": """product_id STRING, product_name STRING, category STRING,
        pack_size STRING, unit_price DOUBLE, unit_cost DOUBLE""",
    "bronze_customers": """customer_id STRING, customer_name STRING, city STRING,
        channel STRING""",
    "bronze_distributors": """distributor_id STRING, distributor_name STRING,
        region STRING, city STRING, target_revenue DOUBLE""",
    "bronze_sales": """sale_date DATE, order_id STRING, product_id STRING,
        distributor_id STRING, city STRING, region STRING, channel STRING,
        units_sold INT, gross_revenue DOUBLE, discount_amount DOUBLE,
        net_revenue DOUBLE, cogs DOUBLE, margin DOUBLE, estimated_demand INT""",
    "bronze_inventory": """inventory_date DATE, product_id STRING, city STRING,
        warehouse STRING, closing_stock INT, safety_stock INT, inventory_value DOUBLE""",
    "bronze_orders": """order_id STRING, order_date DATE, product_id STRING,
        distributor_id STRING, ordered_units INT, fulfilled_units INT, status STRING""",
    "bronze_promotions": """promotion_id STRING, promotion_name STRING,
        product_id STRING, city STRING, start_date DATE, end_date DATE,
        discount_rate DOUBLE""",
    "bronze_forecast": """forecast_date DATE, product_id STRING, city STRING,
        forecast_units INT, model_version STRING""",
}


def py(value):
    if isinstance(value, pd.Timestamp):
        return value.date()
    if hasattr(value, "item"):
        return value.item()
    return value


def rows(frame: pd.DataFrame, columns: list[str]) -> list[tuple]:
    return [tuple(py(value) for value in record) for record in frame[columns].itertuples(index=False, name=None)]


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, date):
        return f"DATE'{value.isoformat()}'"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value)


def insert_batches(cursor, table: str, table_rows: list[tuple], batch_size: int = 500):
    for start in range(0, len(table_rows), batch_size):
        batch = table_rows[start:start + batch_size]
        values = ",".join("(" + ",".join(sql_literal(value) for value in row) + ")" for row in batch)
        cursor.execute(f"INSERT INTO {table} VALUES {values}")


def source_rows():
    data = build_demo_data()
    products = data.products.copy()
    distributors = data.distributors.copy()
    customers = pd.DataFrame([
        (f"C{i:03d}", f"Retail Account {i:03d}", distributor.city,
         ["Traditional Trade", "Modern Trade", "Food Service"][i % 3])
        for i, distributor in enumerate(
            [row for _, row in distributors.iterrows()] * 8, start=1
        )
    ], columns=["customer_id", "customer_name", "city", "channel"])
    sales = data.sales.copy()
    orders = sales[["order_id", "sale_date", "product_id", "distributor_id", "estimated_demand", "units_sold"]].copy()
    orders.columns = ["order_id", "order_date", "product_id", "distributor_id", "ordered_units", "fulfilled_units"]
    orders["status"] = orders.apply(lambda row: "FULFILLED" if row.fulfilled_units >= row.ordered_units * .95 else "PARTIAL", axis=1)
    promotions = data.promotions.merge(products[["product_id", "product_name"]], on="product_name")
    promotions["start_date"] = pd.to_datetime(promotions.start_date)
    promotions["end_date"] = pd.to_datetime(promotions.end_date)
    frames = {
        "bronze_products": (products, ["product_id", "product_name", "category", "pack_size", "unit_price", "unit_cost"]),
        "bronze_customers": (customers, list(customers.columns)),
        "bronze_distributors": (distributors, ["distributor_id", "distributor_name", "region", "city", "target_revenue"]),
        "bronze_sales": (sales, ["sale_date", "order_id", "product_id", "distributor_id", "city", "region", "channel", "units_sold", "gross_revenue", "discount_amount", "net_revenue", "cogs", "margin", "estimated_demand"]),
        "bronze_inventory": (data.inventory, ["inventory_date", "product_id", "city", "warehouse", "closing_stock", "safety_stock", "inventory_value"]),
        "bronze_orders": (orders, list(orders.columns)),
        "bronze_promotions": (promotions, ["promotion_id", "promotion_name", "product_id", "city", "start_date", "end_date", "discount_rate"]),
        "bronze_forecast": (data.forecast, ["forecast_date", "product_id", "city", "forecast_units", "model_version"]),
    }
    return {name: rows(frame, columns) for name, (frame, columns) in frames.items()}


def execute_sql_file(cursor, path: Path, tolerate_errors: bool = False):
    text = path.read_text(encoding="utf-8")
    for statement in (piece.strip() for piece in text.split(";")):
        if not statement:
            continue
        try:
            cursor.execute(statement)
        except Exception as exc:
            if not tolerate_errors:
                raise
            first_line = next((line for line in statement.splitlines() if line.strip() and not line.lstrip().startswith("--")), "statement")
            print(f"GOVERNANCE_WARNING={first_line[:70]} ({type(exc).__name__})")


def main():
    secrets = tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text(encoding="utf-8"))
    connection = sql.connect(
        server_hostname=secrets["DATABRICKS_SERVER_HOSTNAME"],
        http_path=secrets["DATABRICKS_HTTP_PATH"],
        access_token=secrets["DATABRICKS_TOKEN"],
    )
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
        cursor.execute(f"USE CATALOG {CATALOG}")
        cursor.execute(f"USE SCHEMA {SCHEMA}")
        for table, table_rows in source_rows().items():
            cursor.execute(f"CREATE OR REPLACE TABLE {table} ({DDL[table]}) USING DELTA")
            insert_batches(cursor, table, table_rows)
            cursor.execute(f"ALTER TABLE {table} SET TBLPROPERTIES ('kinza.layer'='bronze','kinza.synthetic'='true')")
            print(f"LOADED={table}:{len(table_rows)}", flush=True)
        execute_sql_file(cursor, ROOT / "databricks_assets" / "01_silver_gold.sql")
        execute_sql_file(cursor, ROOT / "databricks_assets" / "02_governance.sql", tolerate_errors=True)
        cursor.execute("SELECT recommended_transfer, protected_revenue FROM gold_transfer_recommendation")
        transfer, revenue = cursor.fetchone()
        print(f"VERIFIED_TRANSFER={int(transfer)}")
        print(f"VERIFIED_PROTECTED_REVENUE={float(revenue):.0f}")
    connection.close()


if __name__ == "__main__":
    main()
