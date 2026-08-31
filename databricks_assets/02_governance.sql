-- Descriptions make the data understandable in Catalog Explorer and improve Genie grounding.
COMMENT ON CATALOG workspace IS 'Governed workspace catalog for the Kinza commercial intelligence prototype';
COMMENT ON SCHEMA workspace.kinza_commercial IS 'Synthetic but business-realistic commercial domain for executive decision intelligence';
COMMENT ON COLUMN workspace.kinza_commercial.gold_inventory_risk.shortage_units IS 'MAX(forecast demand for next 7 days - latest closing stock, 0)';
COMMENT ON COLUMN workspace.kinza_commercial.gold_inventory_risk.days_of_cover IS 'Latest closing stock divided by average daily seven-day forecast';
COMMENT ON COLUMN workspace.kinza_commercial.gold_inventory_risk.revenue_at_risk IS 'Predicted shortage units multiplied by standard unit selling price';
COMMENT ON COLUMN workspace.kinza_commercial.gold_transfer_recommendation.protected_revenue IS 'Recommended transfer units multiplied by standard unit selling price';

ALTER VIEW workspace.kinza_commercial.gold_inventory_risk SET TBLPROPERTIES (
  'kinza.certified'='true', 'kinza.owner'='Supply Chain Analytics', 'kinza.refresh'='daily'
);
ALTER VIEW workspace.kinza_commercial.gold_executive_kpis SET TBLPROPERTIES (
  'kinza.certified'='true', 'kinza.owner'='Commercial Finance', 'kinza.refresh'='daily'
);

-- In an enterprise workspace, replace the demo principal with real account groups.
-- GRANT USE CATALOG ON CATALOG workspace TO `kinza_demo_users`;
-- GRANT USE SCHEMA ON SCHEMA workspace.kinza_commercial TO `kinza_demo_users`;
-- GRANT SELECT ON VIEW workspace.kinza_commercial.gold_inventory_risk TO `kinza_demo_users`;

