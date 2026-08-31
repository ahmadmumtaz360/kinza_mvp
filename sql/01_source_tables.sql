CREATE CATALOG IF NOT EXISTS kinza_demo;
CREATE SCHEMA IF NOT EXISTS kinza_demo.commercial;

CREATE TABLE IF NOT EXISTS kinza_demo.commercial.products (
  product_id STRING, product_name STRING, category STRING, pack_size STRING,
  unit_price DECIMAL(10,2), unit_cost DECIMAL(10,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS kinza_demo.commercial.distributors (
  distributor_id STRING, distributor_name STRING, region STRING, city STRING,
  target_revenue DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS kinza_demo.commercial.sales (
  sale_date DATE, order_id STRING, product_id STRING, distributor_id STRING,
  city STRING, region STRING, channel STRING, units_sold INT,
  gross_revenue DECIMAL(18,2), discount_amount DECIMAL(18,2),
  net_revenue DECIMAL(18,2), cogs DECIMAL(18,2), margin DECIMAL(18,2),
  estimated_demand INT
) USING DELTA;

CREATE TABLE IF NOT EXISTS kinza_demo.commercial.inventory (
  inventory_date DATE, product_id STRING, city STRING, warehouse STRING,
  closing_stock INT, safety_stock INT, inventory_value DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS kinza_demo.commercial.forecast (
  forecast_date DATE, product_id STRING, city STRING, forecast_units INT,
  model_version STRING
) USING DELTA;

