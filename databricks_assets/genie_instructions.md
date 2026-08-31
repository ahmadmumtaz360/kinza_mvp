# Kinza Commercial Genie Agent configuration

Add only these curated assets:

- `workspace.kinza_commercial.gold_executive_kpis`
- `workspace.kinza_commercial.gold_inventory_risk`
- `workspace.kinza_commercial.gold_transfer_recommendation`
- `workspace.kinza_commercial.silver_sales`

General instructions:

1. Currency is Saudi riyals (SAR).
2. Revenue means `SUM(net_revenue)`; never use gross revenue as revenue.
3. Gross margin percentage means `SUM(margin) / SUM(net_revenue)`.
4. A stock-out risk is high when seven-day forecast demand exceeds latest closing stock.
5. Days of cover equals closing stock divided by average daily seven-day forecast.
6. Revenue at risk equals predicted shortage units multiplied by standard unit price.
7. Distinguish demand from fulfilled sales. If estimated demand is stable but fulfilment and inventory fall, classify the decline as supply-driven.
8. State the date range and supporting metrics in every diagnostic answer.
9. Do not invent operational actions. Use `gold_transfer_recommendation` for transfers.

Trusted example question:

> Why did Cola 330ml sales fall in Jeddah, and what action should we take?

Expected reasoning: compare estimated demand, units sold, fulfilment, latest inventory and forecast; identify a supply-driven decline; return the governed transfer and protected revenue.

