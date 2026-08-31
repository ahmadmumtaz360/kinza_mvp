from dataclasses import replace

import pandas as pd
import plotly.express as px
import streamlit as st

from business_logic import QUESTIONS, answer_question, hero_sales_change
from data_model import AS_OF_DATE, HERO_PRODUCT, build_demo_data
from db import connection_status, query_many


st.set_page_config(page_title="Kinza Commercial Intelligence", page_icon="🥤", layout="wide")
data = build_demo_data()
databricks_connected, source_label = connection_status()
if databricks_connected:
    try:
        gold = query_many({
            "executive": "SELECT * FROM workspace.kinza_commercial.gold_executive_kpis",
            "regional": "SELECT * FROM workspace.kinza_commercial.gold_regional_performance",
            "distributor": "SELECT * FROM workspace.kinza_commercial.gold_distributor_performance",
            "risk": "SELECT * FROM workspace.kinza_commercial.gold_inventory_risk",
            "transfer": "SELECT * FROM workspace.kinza_commercial.gold_transfer_recommendation",
            "promotion": "SELECT * FROM workspace.kinza_commercial.gold_promotion_effectiveness",
        })
        risk = gold["risk"]
        risk = risk.rename(columns={"forecast_7d_units": "forecast_units"})
        data = replace(
            data,
            executive_kpis=gold["executive"],
            regional_performance=gold["regional"],
            distributor_performance=gold["distributor"],
            inventory_risk=risk,
            transfer_recommendations=gold["transfer"],
            promotion_effectiveness=gold["promotion"],
        )
    except Exception as exc:
        databricks_connected = False
        source_label = f"Local fallback ({type(exc).__name__})"


def style_chart(figure):
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=12, r=12, t=55, b=18),
        title=dict(font=dict(size=18), x=0.02),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#172A3A", font_color="white"),
        colorway=["#0B8F65", "#19B786", "#F2B84B", "#E66A54", "#526D82"],
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="rgba(128,128,128,.14)", zeroline=False)
    return figure

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
  --kinza-soft: #f4f7f6;
  --kinza-accent: #0b8f65;
  --kinza-shadow: 0 8px 24px rgba(23, 42, 58, .08);
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
    --kinza-soft: #151a1f;
    --kinza-accent: #43d6a3;
    --kinza-shadow: 0 8px 24px rgba(0, 0, 0, .28);
  }
}

.stApp {background-image: radial-gradient(circle at 90% 0%, rgba(11,143,101,.08), transparent 28%);}
.block-container {padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1440px;}
[data-testid="stSidebar"] {border-right: 1px solid var(--kinza-card-border);}
[data-testid="stSidebar"] > div:first-child {padding-top: .5rem;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  padding: .62rem .75rem;
  border-radius: 10px;
  margin-bottom: .18rem;
  transition: background .15s ease, transform .15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(11,143,101,.10);
  transform: translateX(2px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: rgba(11,143,101,.16);
  color: var(--kinza-accent);
  font-weight: 700;
}
.brand-lockup {display:flex;align-items:center;gap:12px;padding:10px 4px 18px;}
.brand-mark {width:44px;height:44px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#0b8f65,#075642);color:white;font-size:24px;font-weight:800;box-shadow:0 8px 20px rgba(11,143,101,.28)}
.brand-name {font-size:1.15rem;font-weight:800;line-height:1.05;letter-spacing:-.02em}
.brand-sub {font-size:.71rem;color:var(--kinza-muted);letter-spacing:.11em;text-transform:uppercase;margin-top:5px}
.eyebrow {font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#47d3a3;margin-bottom:8px}
.page-kicker {display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--kinza-card-border);padding-bottom:12px;margin-bottom:18px;color:var(--kinza-muted);font-size:.82rem}
.live-dot {display:inline-block;width:8px;height:8px;border-radius:50%;background:#32c48d;box-shadow:0 0 0 5px rgba(50,196,141,.14);margin-right:8px}
.source-card {background:var(--kinza-card);border:1px solid var(--kinza-card-border);border-radius:12px;padding:12px 13px;margin:14px 0;color:var(--kinza-card-text);box-shadow:var(--kinza-shadow)}
.source-label {font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:var(--kinza-muted);font-weight:700}
.source-value {font-size:.82rem;font-weight:700;margin-top:6px}
.sidebar-foot {font-size:.72rem;color:var(--kinza-muted);border-top:1px solid var(--kinza-card-border);padding-top:14px;margin-top:20px;line-height:1.7}
[data-testid="stMetric"] {
  background: var(--kinza-card);
  border: 1px solid var(--kinza-card-border);
  border-radius: 14px;
  padding: 16px 17px;
  color: var(--kinza-card-text);
  box-shadow: var(--kinza-shadow);
  min-height: 112px;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]:before {content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(#19b786,#0b6b54)}
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
  color: var(--kinza-card-text);
}
.hero {
  background: linear-gradient(125deg, var(--kinza-hero-start), var(--kinza-hero-end));
  color: var(--kinza-hero-text);
  padding: 30px 32px;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: 22px;
  margin-bottom: 22px;
  box-shadow: 0 18px 45px rgba(7,86,66,.20);
  position:relative;
  overflow:hidden;
}
.hero:after {content:"";position:absolute;width:220px;height:220px;border-radius:50%;right:-70px;top:-105px;background:rgba(255,255,255,.08)}
.hero h1,.hero h2 {letter-spacing:-.035em;margin-bottom:8px}
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
[data-testid="stDataFrame"] {border:1px solid var(--kinza-card-border);border-radius:14px;overflow:hidden;box-shadow:var(--kinza-shadow)}
[data-testid="stPlotlyChart"] {background:var(--kinza-card);border:1px solid var(--kinza-card-border);border-radius:16px;padding:5px;box-shadow:var(--kinza-shadow)}
.stButton > button {border-radius:10px;font-weight:700;min-height:42px;border:1px solid var(--kinza-card-border);transition:transform .15s ease,box-shadow .15s ease}
.stButton > button:hover {transform:translateY(-1px);box-shadow:0 8px 20px rgba(11,143,101,.16);border-color:var(--kinza-accent)}
h1,h2,h3 {letter-spacing:-.025em;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""<div class="brand-lockup"><div class="brand-mark">K</div><div><div class="brand-name">Kinza</div><div class="brand-sub">Commercial Intelligence</div></div></div>""", unsafe_allow_html=True)
navigation = {
    "⌂  Executive Overview": "Executive Overview",
    "◫  Sales & Distribution": "Sales & Distribution",
    "◈  Inventory Intelligence": "Inventory Intelligence",
    "✓  Action Center": "Action Center",
    "✦  Ask Your Business": "Ask Your Business",
    "◇  Data Trust": "Data Trust",
}
choice = st.sidebar.radio("Navigation", list(navigation), label_visibility="collapsed")
page = navigation[choice]
status_dot = "<span class='live-dot'></span>" if databricks_connected else "● "
st.sidebar.markdown(f"""<div class="source-card"><div class="source-label">Data foundation</div><div class="source-value">{status_dot}{source_label}</div></div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"""<div class="sidebar-foot"><b>Scope</b><br>KSA · All regions · Last 6 months<br><br><b>Data current through</b><br>{AS_OF_DATE:%d %B %Y}</div>""", unsafe_allow_html=True)

st.markdown(f"<div class='page-kicker'><span>COMMERCIAL COMMAND CENTER</span><span><span class='live-dot'></span>DATA REFRESHED · {AS_OF_DATE:%d %b %Y}</span></div>", unsafe_allow_html=True)

if page == "Executive Overview":
    st.markdown('<div class="hero"><div class="eyebrow">Executive pulse</div><h1>See the business. Decide what happens next.</h1><p>A decision-ready view of growth, margin and commercial risk across the Kingdom.</p></div>', unsafe_allow_html=True)
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
    left.plotly_chart(style_chart(px.line(monthly, x="month", y="net_revenue", markers=True, title="Revenue trend")), width="stretch")
    right.plotly_chart(style_chart(px.bar(data.regional_performance, x="region", y="revenue", color="growth", title="Revenue by region", color_continuous_scale="RdYlGn")), width="stretch")
    decline = hero_sales_change(data)
    st.warning(f"Attention required: {HERO_PRODUCT} unit sales in Jeddah fell {abs(decline):.0%}. Inventory availability—not customer demand—is the primary driver.")

elif page == "Sales & Distribution":
    st.title("Sales & Distribution")
    st.caption("Where growth is coming from, and which partners need intervention.")
    left, right = st.columns(2)
    left.plotly_chart(style_chart(px.bar(data.regional_performance, x="city", y="revenue", color="margin_pct", title="Regional revenue and margin", color_continuous_scale="Blues")), width="stretch")
    channel = data.sales[data.sales.sale_date >= "2026-07-01"].groupby("channel", as_index=False).agg(revenue=("net_revenue", "sum"), margin=("margin", "sum"))
    channel["margin_pct"] = channel.margin / channel.revenue
    right.plotly_chart(style_chart(px.scatter(channel, x="revenue", y="margin_pct", size="revenue", text="channel", title="Channel performance")), width="stretch")
    view = data.distributor_performance.copy()
    for col in ["growth", "margin_pct", "fill_rate", "return_rate"]:
        view[col] = view[col].map(lambda x: f"{x:.1%}")
    st.subheader("Distributor scorecard")
    st.dataframe(view[["distributor_name", "city", "revenue", "growth", "margin_pct", "fill_rate", "return_rate", "stock_outs", "score"]], hide_index=True, width="stretch")
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
    st.plotly_chart(style_chart(px.area(history, x="inventory_date", y="closing_stock", title="Jeddah inventory depletion")), width="stretch")
    st.markdown(f"""<div class="action"><h3>Recommended action</h3><p>Transfer <b>{transfer.recommended_transfer:,.0f} units</b> from Riyadh to Jeddah.</p><p>Riyadh stock after transfer: <b>{transfer.source_stock_after:,.0f}</b> (safety stock: {transfer.source_safety_stock:,.0f}).</p><h2>SAR {transfer.protected_revenue:,.0f} sales protected</h2></div>""", unsafe_allow_html=True)
    st.subheader("Risk queue")
    st.dataframe(data.inventory_risk[["product_name", "city", "closing_stock", "forecast_units", "shortage_units", "days_of_cover", "risk_level", "revenue_at_risk"]], hide_index=True, width="stretch")

elif page == "Action Center":
    st.title("Executive Action Center")
    st.caption("Prioritized decisions—not another dashboard.")
    transfer = data.transfer_recommendations.iloc[0]
    actions = pd.DataFrame([
        {"priority": "P1", "decision": "Rebalance Cola 330ml inventory", "owner": "Supply Chain", "due": "Today", "value": transfer.protected_revenue, "confidence": .94, "status": "Recommended"},
        {"priority": "P1", "decision": "Review Al Noor service recovery plan", "owner": "Sales Director", "due": "48 hours", "value": 126_000, "confidence": .88, "status": "Needs review"},
        {"priority": "P2", "decision": "Stop Riyadh margin-dilutive promotion", "owner": "Revenue Growth", "due": "This week", "value": 91_000, "confidence": .91, "status": "Recommended"},
    ])
    cols = st.columns(3)
    cols[0].metric("Open Decisions", len(actions))
    cols[1].metric("Value Addressable", f"SAR {actions.value.sum()/1_000:.0f}k")
    cols[2].metric("High-confidence Actions", int((actions.confidence >= .9).sum()))
    for index, row in actions.iterrows():
        with st.container(border=True):
            left, middle, right = st.columns([5, 2, 2])
            left.subheader(f"{row.priority} · {row.decision}")
            left.caption(f"Owner: {row.owner} · Due: {row.due}")
            middle.metric("Potential value", f"SAR {row.value/1_000:.0f}k")
            right.metric("Confidence", f"{row.confidence:.0%}")
            key = f"action_{index}"
            if st.button("Mark reviewed", key=key):
                st.session_state[key] = True
            if st.session_state.get(key):
                st.success("Reviewed in this demo session. Production approval would be written to an operational workflow table.")

elif page == "Ask Your Business":
    st.title("Ask Your Business")
    st.caption("Evidence-backed commercial Q&A grounded in governed metric definitions.")
    question = st.selectbox("Ask a question", QUESTIONS)
    if st.button("Analyze", type="primary", width="stretch"):
        st.markdown(answer_question(question, data))
    with st.expander("Why the answers are reliable"):
        st.write("Each demo answer maps to governed business calculations. In Databricks, the same curated Gold views and definitions are supplied to a narrowly scoped Genie Agent.")

else:
    st.title("Data Trust")
    st.caption("The business insight is only valuable when every number is explainable.")
    cols = st.columns(4)
    cols[0].metric("Certified Metrics", "9")
    cols[1].metric("Data Quality", "99.2%")
    cols[2].metric("Freshness", "Daily")
    cols[3].metric("Policy Violations", "0")
    st.subheader("Lineage of the SAR 184k recommendation")
    st.markdown("""
    **ERP, distributor and warehouse sources**  
    ↓ `bronze_sales`, `bronze_inventory`, `bronze_orders`, `bronze_forecast`  
    ↓ validated and conformed in `silver_sales` and `silver_inventory`  
    ↓ governed calculation in `gold_inventory_risk`  
    ↓ decision rule in `gold_transfer_recommendation`  
    ↓ **8,500 units recommended · SAR 184,000 protected sales**
    """)
    st.subheader("Governed business definitions")
    definitions = pd.DataFrame([
        ("Revenue", "SUM(net_revenue)", "Commercial Finance", "Certified"),
        ("Gross Margin %", "SUM(margin) / SUM(net_revenue)", "Commercial Finance", "Certified"),
        ("Days of Cover", "closing_stock / average daily 7-day forecast", "Supply Chain", "Certified"),
        ("Revenue at Risk", "shortage_units × standard unit price", "Supply Chain", "Certified"),
        ("Protected Revenue", "recommended transfer × standard unit price", "Commercial Finance", "Certified"),
    ], columns=["metric", "definition", "owner", "status"])
    st.dataframe(definitions, hide_index=True, width="stretch")
    st.info("Open Catalog Explorer in Databricks during the demonstration to reveal owners, table and column descriptions, properties, permissions, and automatically captured lineage.")
