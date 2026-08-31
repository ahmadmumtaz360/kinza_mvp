# Kinza customer demo runbook

Target duration: 10–12 minutes. Keep the first eight minutes commercial and reveal
Databricks only after the recommendation has landed.

## 1. Executive signal (90 seconds)

Open **Executive Overview**. Establish that the overall business is healthy, then
focus on the alert: Cola 330ml sales in Jeddah have fallen sharply.

Say: “A dashboard tells us what moved. Kinza needs to know why, what happens next,
and which decision protects value.”

## 2. Explain the decline (90 seconds)

Open **Ask Your Business** and select “Why did Cola 330ml sales fall in Jeddah?”
Emphasize that forecast demand remains healthy while inventory and fulfilment fall.
The conclusion is supply-driven, not demand-driven.

## 3. Predict and act (2 minutes)

Open **Inventory Intelligence**. Show:

- 4,500 current units
- 13,000 forecast units for seven days
- 8,500-unit predicted shortage
- 25,000-unit excess in Riyadh before transfer
- 8,500-unit Riyadh-to-Jeddah recommendation
- SAR 184,000 protected sales

## 4. Manage the decisions (90 seconds)

Open **Action Center**. Show that insights are prioritized with an owner, due date,
confidence, and financial value. Mark the inventory recommendation reviewed.

## 5. Broaden the commercial story (90 seconds)

Open **Sales & Distribution**. Highlight Al Noor’s weak service score. Ask which
promotion destroyed margin to reveal the Riyadh volume/margin tradeoff.

## 6. Reveal the platform and trust (2 minutes)

Open **Data Trust**, then switch to Databricks Catalog Explorer:

1. Show the eight Bronze source tables.
2. Show the Silver conformed tables.
3. Open `gold_transfer_recommendation` and its descriptions/properties.
4. Open lineage and trace the view back to inventory, forecast, and products.
5. Show the Genie Agent’s limited curated asset list and metric instructions.

Close with: “The interface can change. The governed definitions, lineage, security,
and reusable intelligence underneath it are the durable product.”

