# Databricks notebook source
# MAGIC %md
# MAGIC # Kinza Commercial Intelligence — deterministic data setup
# MAGIC Run this notebook on serverless compute. It creates eight governed source
# MAGIC tables in Unity Catalog and deliberately plants the customer demo stories.

# COMMAND ----------
from datetime import date, timedelta
import math
import random

from pyspark.sql import Row
from pyspark.sql import functions as F

CATALOG = "workspace"  # Change if your workspace uses another writable catalog.
SCHEMA = "kinza_commercial"
AS_OF = date(2026, 8, 1)
random.seed(17)

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

products = [
    Row(product_id="P001", product_name="Cola 330ml", category="Cola", pack_size="330ml", unit_price=184000/8500, unit_cost=12.20),
    Row(product_id="P002", product_name="Cola 500ml", category="Cola", pack_size="500ml", unit_price=27.00, unit_cost=15.00),
    Row(product_id="P003", product_name="Lemon 330ml", category="Citrus", pack_size="330ml", unit_price=20.00, unit_cost=11.10),
    Row(product_id="P004", product_name="Orange 330ml", category="Citrus", pack_size="330ml", unit_price=20.50, unit_cost=11.30),
    Row(product_id="P005", product_name="Diet Cola 330ml", category="Cola", pack_size="330ml", unit_price=22.00, unit_cost=12.80),
]
distributors = [
    Row(distributor_id="D01", distributor_name="Red Sea Trading", region="West", city="Jeddah", target_revenue=8_000_000.0),
    Row(distributor_id="D02", distributor_name="Central Route Co.", region="Central", city="Riyadh", target_revenue=9_200_000.0),
    Row(distributor_id="D03", distributor_name="Al Noor Distribution", region="East", city="Dammam", target_revenue=6_800_000.0),
    Row(distributor_id="D04", distributor_name="Northern Markets", region="North", city="Tabuk", target_revenue=4_500_000.0),
    Row(distributor_id="D05", distributor_name="Southern Supply", region="South", city="Abha", target_revenue=4_200_000.0),
]
customers = [Row(customer_id=f"C{i:03}", customer_name=f"Retail Account {i:03}", city=d.city, channel=["Traditional Trade", "Modern Trade", "Food Service"][i % 3]) for i, d in enumerate(distributors * 8, 1)]

product_by_id = {p.product_id: p for p in products}
sales, orders = [], []
order_number = 1
for offset in range(181):
    day = date(2026, 2, 1) + timedelta(days=offset)
    seasonal = 1 + .09 * math.sin((day.timetuple().tm_yday - 90) / 365 * 2 * math.pi)
    for d_idx, distributor in enumerate(distributors):
        for p_idx, product in enumerate(products):
            demand = int((210 + 20*p_idx + 14*d_idx) * seasonal * random.uniform(.94, 1.06))
            availability = .30 if product.product_id == "P001" and distributor.city == "Jeddah" and day >= date(2026, 7, 25) else (.52 if product.product_id == "P001" and distributor.city == "Jeddah" and day >= date(2026, 7, 18) else 1)
            units = int(demand * availability)
            discount = .33 if product.product_id == "P002" and distributor.city == "Riyadh" and day >= date(2026, 7, 1) else .04
            if discount == .33: units = int(units * 1.42)
            gross = units * product.unit_price
            net = gross * (1-discount)
            order_id = f"SO{order_number:07d}"
            orders.append(Row(order_id=order_id, order_date=day, product_id=product.product_id, distributor_id=distributor.distributor_id, ordered_units=demand, fulfilled_units=units, status="FULFILLED" if units >= demand*.95 else "PARTIAL"))
            sales.append(Row(sale_date=day, order_id=order_id, product_id=product.product_id, distributor_id=distributor.distributor_id, city=distributor.city, region=distributor.region, units_sold=units, gross_revenue=float(gross), discount_amount=float(gross-net), net_revenue=float(net), cogs=float(units*product.unit_cost), margin=float(net-units*product.unit_cost), estimated_demand=demand))
            order_number += 1

inventory, forecast = [], []
jeddah_stock = [28000,25000,21000,17000,14000,11000,8500,6500,5300,5000,4800,4650,4500]
for offset in range(13):
    day = date(2026, 7, 20) + timedelta(days=offset)
    for distributor in distributors:
        for product in products:
            if product.product_id == "P001" and distributor.city == "Jeddah": closing, safety = jeddah_stock[offset], 10000
            elif product.product_id == "P001" and distributor.city == "Riyadh": closing, safety = 40000, 15000
            else: closing, safety = random.randint(13000, 31000), 9000
            inventory.append(Row(inventory_date=day, product_id=product.product_id, city=distributor.city, warehouse=f"{distributor.city} DC", closing_stock=closing, safety_stock=safety, inventory_value=float(closing*product.unit_cost)))

for distributor in distributors:
    for product in products:
        weekly = [1850]*6+[1900] if product.product_id == "P001" and distributor.city == "Jeddah" else [random.randint(850,1550) for _ in range(7)]
        for offset, units in enumerate(weekly):
            forecast.append(Row(forecast_date=AS_OF+timedelta(days=offset), product_id=product.product_id, city=distributor.city, forecast_units=units, model_version="demo-v1"))

promotions = [Row(promotion_id="PR01", promotion_name="Cola 500ml Riyadh Volume Push", product_id="P002", city="Riyadh", start_date=date(2026,7,1), end_date=date(2026,7,31), discount_rate=.33), Row(promotion_id="PR02", promotion_name="Citrus Summer Bundle", product_id="P003", city="Jeddah", start_date=date(2026,6,1), end_date=date(2026,6,30), discount_rate=.08)]

tables = {"products":products, "customers":customers, "distributors":distributors, "sales":sales, "inventory":inventory, "orders":orders, "promotions":promotions, "forecast":forecast}
for name, rows in tables.items():
    spark.createDataFrame(rows).write.mode("overwrite").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.bronze_{name}")
    spark.sql(f"ALTER TABLE {CATALOG}.{SCHEMA}.bronze_{name} SET TBLPROPERTIES ('kinza.layer'='bronze', 'kinza.synthetic'='true')")

display(spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}"))

