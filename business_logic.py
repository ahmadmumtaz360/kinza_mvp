from __future__ import annotations

import pandas as pd

from data_model import DemoData, HERO_PRODUCT


QUESTIONS = [
    "Why did Cola 330ml sales fall in Jeddah?",
    "Was the decline demand- or supply-driven?",
    "Which SKUs are at highest stock-out risk?",
    "Which distributor is underperforming?",
    "Which promotion destroyed margin?",
]


def hero_sales_change(data: DemoData) -> float:
    hero = data.sales[(data.sales.product_name == HERO_PRODUCT) & (data.sales.city == "Jeddah")]
    recent = hero[(hero.sale_date >= pd.Timestamp("2026-07-18")) & (hero.sale_date <= pd.Timestamp("2026-07-31"))].units_sold.sum()
    prior = hero[(hero.sale_date >= pd.Timestamp("2026-07-04")) & (hero.sale_date <= pd.Timestamp("2026-07-17"))].units_sold.sum()
    return recent / prior - 1


def answer_question(question: str, data: DemoData) -> str:
    transfer = data.transfer_recommendations.iloc[0]
    hero = data.inventory_risk[(data.inventory_risk.product_name == HERO_PRODUCT) & (data.inventory_risk.city == "Jeddah")].iloc[0]
    decline = hero_sales_change(data)
    if question in QUESTIONS[:2]:
        return (
            f"**The decline is supply-driven.** Cola 330ml unit sales in Jeddah fell {abs(decline):.0%} in the recent two-week period, "
            f"while forecast demand remains at {hero.forecast_units:,.0f} units for the next seven days. Current stock is only "
            f"{hero.closing_stock:,.0f} units, leaving a predicted shortage of {hero.shortage_units:,.0f} units.\n\n"
            f"**Recommended action:** transfer {transfer.recommended_transfer:,.0f} units from Riyadh to Jeddah. "
            f"Estimated sales protected: **SAR {transfer.protected_revenue:,.0f}**."
        )
    if question == QUESTIONS[2]:
        high = data.inventory_risk[data.inventory_risk.risk_level == "HIGH"].head(3)
        lines = [f"- {r.product_name} — {r.city}: {r.shortage_units:,.0f} units, SAR {r.revenue_at_risk:,.0f} at risk" for _, r in high.iterrows()]
        return "**Highest current stock-out risks:**\n\n" + "\n".join(lines)
    if question == QUESTIONS[3]:
        bad = data.distributor_performance.sort_values("score").iloc[0]
        return (f"**{bad.distributor_name} requires attention.** Its commercial score is {bad.score}/100, fill rate is "
                f"{bad.fill_rate:.0%}, returns are {bad.return_rate:.0%}, and it recorded {bad.stock_outs} stock-outs.")
    promo = data.promotion_effectiveness.iloc[0]
    return (f"**{promo.promotion_name} traded margin for volume.** Volume rose {promo.volume_lift:.0%}, but margin fell from "
            f"{promo.baseline_margin_pct:.1%} to {promo.margin_pct:.1%}; estimated ROI is {promo.roi:.2f}x.")

