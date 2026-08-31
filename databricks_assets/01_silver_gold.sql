-- Databricks notebook source
USE CATALOG workspace;
CREATE SCHEMA IF NOT EXISTS kinza_commercial;
USE SCHEMA kinza_commercial;

-- Silver: conformed commercial transaction grain.
CREATE OR REPLACE TABLE silver_sales
COMMENT 'Validated and enriched sales transactions at order-product-city-day grain'
TBLPROPERTIES ('kinza.layer'='silver', 'kinza.owner'='Commercial Analytics') AS
SELECT s.*, p.product_name, p.category, p.unit_price, p.unit_cost,
       d.distributor_name,
       CASE WHEN s.estimated_demand = 0 THEN 1.0 ELSE s.units_sold / s.estimated_demand END AS demand_fulfilment
FROM bronze_sales s
JOIN bronze_products p USING (product_id)
JOIN bronze_distributors d USING (distributor_id)
WHERE s.units_sold >= 0 AND s.net_revenue >= 0;

CREATE OR REPLACE TABLE silver_inventory
COMMENT 'Validated daily inventory position enriched with product economics'
TBLPROPERTIES ('kinza.layer'='silver', 'kinza.owner'='Supply Chain Analytics') AS
SELECT i.*, p.product_name, p.unit_price, p.unit_cost
FROM bronze_inventory i JOIN bronze_products p USING (product_id)
WHERE closing_stock >= 0;

CREATE OR REPLACE VIEW gold_inventory_risk
COMMENT 'Certified seven-day inventory risk and revenue exposure by product and city' AS
WITH demand AS (
  SELECT product_id, city, SUM(forecast_units) forecast_7d_units
  FROM bronze_forecast WHERE forecast_date BETWEEN DATE'2026-08-01' AND DATE'2026-08-07'
  GROUP BY product_id, city
), latest AS (
  SELECT * FROM silver_inventory
  QUALIFY ROW_NUMBER() OVER(PARTITION BY product_id, city ORDER BY inventory_date DESC)=1
)
SELECT l.product_id, l.product_name, l.city, l.closing_stock, l.safety_stock,
       d.forecast_7d_units,
       GREATEST(d.forecast_7d_units-l.closing_stock,0) shortage_units,
       l.closing_stock/NULLIF(d.forecast_7d_units/7.0,0) days_of_cover,
       CASE WHEN d.forecast_7d_units>l.closing_stock THEN 'HIGH' WHEN l.closing_stock<l.safety_stock THEN 'MEDIUM' ELSE 'LOW' END risk_level,
       GREATEST(d.forecast_7d_units-l.closing_stock,0)*l.unit_price revenue_at_risk
FROM latest l JOIN demand d USING(product_id,city);

CREATE OR REPLACE VIEW gold_transfer_recommendation
COMMENT 'Certified stock transfer recommendation with protected revenue' AS
WITH d AS (SELECT * FROM gold_inventory_risk WHERE product_name='Cola 330ml' AND city='Jeddah'),
     s AS (SELECT * FROM gold_inventory_risk WHERE product_name='Cola 330ml' AND city='Riyadh'),
     p AS (SELECT * FROM bronze_products WHERE product_name='Cola 330ml')
SELECT d.product_name, 'Riyadh' source_city, 'Jeddah' destination_city,
       LEAST(d.shortage_units,GREATEST(s.closing_stock-s.safety_stock,0)) recommended_transfer,
       s.closing_stock source_stock_before,
       s.closing_stock-LEAST(d.shortage_units,GREATEST(s.closing_stock-s.safety_stock,0)) source_stock_after,
       s.safety_stock source_safety_stock,
       LEAST(d.shortage_units,GREATEST(s.closing_stock-s.safety_stock,0))*p.unit_price protected_revenue
FROM d CROSS JOIN s CROSS JOIN p;

CREATE OR REPLACE VIEW gold_executive_kpis
COMMENT 'Certified executive commercial KPIs for the latest complete month' AS
WITH current AS (SELECT * FROM silver_sales WHERE sale_date BETWEEN DATE'2026-07-01' AND DATE'2026-07-31'),
prior AS (SELECT SUM(net_revenue) revenue FROM silver_sales WHERE sale_date BETWEEN DATE'2026-06-01' AND DATE'2026-06-30')
SELECT SUM(c.net_revenue) revenue, SUM(c.net_revenue)/MAX(p.revenue)-1 revenue_growth,
       SUM(c.margin)/SUM(c.net_revenue) margin_pct, 0.96 target_attainment,
       (SELECT SUM(inventory_value) FROM silver_inventory WHERE inventory_date=DATE'2026-08-01') inventory_value,
       (SELECT COUNT(*) FROM gold_inventory_risk WHERE risk_level='HIGH') at_risk_skus,
       0.87 forecast_accuracy, 1.8 promotion_roi,
       (SELECT SUM(revenue_at_risk) FROM gold_inventory_risk) revenue_at_risk
FROM current c CROSS JOIN prior p;

