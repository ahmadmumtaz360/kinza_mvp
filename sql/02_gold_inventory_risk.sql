CREATE OR REPLACE VIEW kinza_demo.commercial.gold_inventory_risk AS
WITH demand AS (
  SELECT product_id, city, SUM(forecast_units) AS forecast_7d_units
  FROM kinza_demo.commercial.forecast
  WHERE forecast_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-07'
  GROUP BY product_id, city
), latest_inventory AS (
  SELECT product_id, city, closing_stock, safety_stock, inventory_value
  FROM kinza_demo.commercial.inventory
  QUALIFY ROW_NUMBER() OVER (PARTITION BY product_id, city ORDER BY inventory_date DESC) = 1
)
SELECT d.product_id, p.product_name, d.city, i.closing_stock, i.safety_stock,
       d.forecast_7d_units,
       GREATEST(d.forecast_7d_units - i.closing_stock, 0) AS shortage_units,
       i.closing_stock / NULLIF(d.forecast_7d_units / 7.0, 0) AS days_of_cover,
       CASE WHEN d.forecast_7d_units > i.closing_stock THEN 'HIGH'
            WHEN i.closing_stock < i.safety_stock THEN 'MEDIUM' ELSE 'LOW' END AS risk_level,
       GREATEST(d.forecast_7d_units - i.closing_stock, 0) * p.unit_price AS revenue_at_risk
FROM demand d
JOIN latest_inventory i USING (product_id, city)
JOIN kinza_demo.commercial.products p USING (product_id);

