import pandas as pd
import plotly.express as px
import streamlit as st

from business_logic import QUESTIONS, answer_question, hero_sales_change
from data_model import AS_OF_DATE, HERO_PRODUCT, build_demo_data


st.set_page_config(page_title="Kinza Commercial Intelligence", page_icon="🥤", layout="wide")
data = build_demo_data()

st.markdown("""
<style>
:root {
  color-scheme: light dark;
  --kinza-card: rgba(255, 255, 255, 0.92);
  --kinza-card-border: #dfe3e8;
  --kinza-card-text: #17202a;
  --kinza-muted: #52606d;
  --kinza-hero-start: #172a3a;
  --kinza-hero-end: #0b6b54;
  --kinza-hero-text: #ffffff;
  --kinza-action: #effaf5;
  --kinza-action-border: #0b8f65;
  --kinza-action-text: #12372d;
  --kinza-risk: #ffb4ab;
}

@media (prefers-color-scheme: dark) {
  :root {
    --kinza-card: rgba(30, 34, 39, 0.96);
    --kinza-card-border: #49515a;
    --kinza-card-text: #f5f7f9;
    --kinza-muted: #c3cad2;
    --kinza-hero-start: #12212d;
    --kinza-hero-end: #075642;
    --kinza-action: #132d26;
    --kinza-action-border: #43d6a3;
    --kinza-action-text: #eefbf6;
    --kinza-risk: #ffb4ab;
  }
}

.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
  background: var(--kinza-card);
  border: 1px solid var(--kinza-card-border);
  border-radius: 14px;
  padding: 14px;
  color: var(--kinza-card-text);
}
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
  color: var(--kinza-card-text);
}
.hero {
  background: linear-gradient(125deg, var(--kinza-hero-start), var(--kinza-hero-end));
  color: var(--kinza-hero-text);
  padding: 24px;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: 18px;
  margin-bottom: 18px;
}
.hero h1, .hero h2, .hero p {color: var(--kinza-hero-text) !important;}
.action {
  background: var(--kinza-action);
  color: var(--kinza-action-text);
  border: 1px solid var(--kinza-card-border);
  border-left: 5px solid var(--kinza-action-border);
  padding: 18px;
  border-radius: 10px;
}
.action h2, .action h3, .action p {color: var(--kinza-action-text) !important;}
.risk {color: var(--kinza-risk) !important;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Kinza")
page = st.sidebar.radio("Commercial Intelligence", ["Executive Overview", "Sales & Distribution", "Inventory Intelligence", "Ask Your Business"])
st.sidebar.caption(f"Demo data as of {AS_OF_DATE:%d %b %Y}")

if page == "Executive Overview":
    st.markdown('<div class="hero"><h1>Executive Overview</h1><p>A decision-ready view of growth, margin and commercial risk.</p></div>', unsafe_allow_html=True)
    k = data.executive_kpis.iloc[0]
    cols = st.columns(4)
    cols[0].metric("Revenue", f"SAR {k.revenue/1_000_000:.1f}M", f"{k.revenue_growth:+.1%}")
    cols[1].metric("Gross Margin", f"{k.margin_pct:.1%}")
    cols[2].metric("Target Attainment", f"{k.target_attainment:.0%}")
    cols[3].metric("At-risk SKUs", f"{int(k.at_risk_skus)}")
    cols = st.columns(4)
    cols[0].metric("Inventory Value", f"SAR {k.inventory_value/1_000_000:.1f}M")
    cols[1].metric("Forecast Accuracy", f"{k.forecast_accuracy:.0%}")
    cols[2].metric("Promotion ROI", f"{k.promotion_roi:.1f}x")
    cols[3].metric("Revenue at Risk", f"SAR {k.revenue_at_risk/1_000:.0f}k")
    left, right = st.columns(2)
    monthly = data.sales.assign(month=lambda x: x.sale_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).net_revenue.sum()
    left.plotly_chart(px.line(monthly, x="month", y="net_revenue", markers=True, title="Revenue trend"), use_container_width=True)
    right.plotly_chart(px.bar(data.regional_performance, x="region", y="revenue", color="growth", title="Revenue by region", color_continuous_scale="RdYlGn"), use_container_width=True)
    decline = hero_sales_change(data)
    st.warning(f"Attention required: {HERO_PRODUCT} unit sales in Jeddah fell {abs(decline):.0%}. Inventory availability—not customer demand—is the primary driver.")

elif page == "Sales & Distribution":
    st.title("Sales & Distribution")
    st.caption("Where growth is coming from, and which partners need intervention.")
    left, right = st.columns(2)
    left.plotly_chart(px.bar(data.regional_performance, x="city", y="revenue", color="margin_pct", title="Regional revenue and margin", color_continuous_scale="Blues"), use_container_width=True)
    channel = data.sales[data.sales.sale_date >= "2026-07-01"].groupby("channel", as_index=False).agg(revenue=("net_revenue", "sum"), margin=("margin", "sum"))
    channel["margin_pct"] = channel.margin / channel.revenue
    right.plotly_chart(px.scatter(channel, x="revenue", y="margin_pct", size="revenue", text="channel", title="Channel performance"), use_container_width=True)
    view = data.distributor_performance.copy()
    for col in ["growth", "margin_pct", "fill_rate", "return_rate"]:
        view[col] = view[col].map(lambda x: f"{x:.1%}")
    st.subheader("Distributor scorecard")
    st.dataframe(view[["distributor_name", "city", "revenue", "growth", "margin_pct", "fill_rate", "return_rate", "stock_outs", "score"]], hide_index=True, use_container_width=True)
    st.error("Al Noor Distribution is deteriorating: 84% fill rate, 6% returns, 12 stock-outs and a 62/100 score.")

elif page == "Inventory Intelligence":
    st.title("Inventory Intelligence")
    hero = data.inventory_risk[(data.inventory_risk.product_name == HERO_PRODUCT) & (data.inventory_risk.city == "Jeddah")].iloc[0]
    transfer = data.transfer_recommendations.iloc[0]
    st.markdown(f'<div class="hero"><h2>{HERO_PRODUCT} — Jeddah</h2><p class="risk">HIGH STOCK-OUT RISK</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Current Stock", f"{hero.closing_stock:,.0f}")
    cols[1].metric("Forecast Demand (7d)", f"{hero.forecast_units:,.0f}")
    cols[2].metric("Days of Cover", f"{hero.days_of_cover:.1f}")
    cols[3].metric("Predicted Shortage", f"{hero.shortage_units:,.0f}")
    history = data.inventory[(data.inventory.product_name == HERO_PRODUCT) & (data.inventory.city == "Jeddah")]
    st.plotly_chart(px.area(history, x="inventory_date", y="closing_stock", title="Jeddah inventory depletion"), use_container_width=True)
    st.markdown(f"""<div class="action"><h3>Recommended action</h3><p>Transfer <b>{transfer.recommended_transfer:,.0f} units</b> from Riyadh to Jeddah.</p><p>Riyadh stock after transfer: <b>{transfer.source_stock_after:,.0f}</b> (safety stock: {transfer.source_safety_stock:,.0f}).</p><h2>SAR {transfer.protected_revenue:,.0f} sales protected</h2></div>""", unsafe_allow_html=True)
    st.subheader("Risk queue")
    st.dataframe(data.inventory_risk[["product_name", "city", "closing_stock", "forecast_units", "shortage_units", "days_of_cover", "risk_level", "revenue_at_risk"]], hide_index=True, use_container_width=True)

else:
    st.title("Ask Your Business")
    st.caption("Constrained, evidence-backed commercial Q&A for a reliable executive demo.")
    question = st.selectbox("Ask a question", QUESTIONS)
    if st.button("Analyze", type="primary", use_container_width=True):
        st.markdown(answer_question(question, data))
    with st.expander("Why the answers are reliable"):
        st.write("Each question maps to governed business calculations over the curated presentation datasets. No unrestricted text-to-SQL is used in this MVP.")
