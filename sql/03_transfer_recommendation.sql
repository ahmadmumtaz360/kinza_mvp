CREATE OR REPLACE VIEW kinza_demo.commercial.gold_inventory_transfer_recommendation AS
WITH risks AS (
  SELECT * FROM kinza_demo.commercial.gold_inventory_risk
), destination AS (
  SELECT * FROM risks WHERE product_name = 'Cola 330ml' AND city = 'Jeddah'
), source AS (
  SELECT * FROM risks WHERE product_name = 'Cola 330ml' AND city = 'Riyadh'
)
SELECT d.product_id, d.product_name, 'Riyadh' AS source_city, 'Jeddah' AS destination_city,
       LEAST(d.shortage_units, GREATEST(s.closing_stock - s.safety_stock, 0)) AS recommended_transfer,
       LEAST(d.shortage_units, GREATEST(s.closing_stock - s.safety_stock, 0)) * p.unit_price AS protected_revenue
FROM destination d CROSS JOIN source s
JOIN kinza_demo.commercial.products p ON p.product_id = d.product_id;
