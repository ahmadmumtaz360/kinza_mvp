from business_logic import hero_sales_change
from data_model import HERO_PRODUCT, build_demo_data


data = build_demo_data()
hero = data.inventory_risk[(data.inventory_risk.product_name == HERO_PRODUCT) & (data.inventory_risk.city == "Jeddah")].iloc[0]
transfer = data.transfer_recommendations.iloc[0]
bad_distributor = data.distributor_performance.sort_values("score").iloc[0]
promo = data.promotion_effectiveness.iloc[0]

assert hero.closing_stock == 4_500
assert hero.forecast_units == 13_000
assert hero.shortage_units == 8_500
assert transfer.recommended_transfer == 8_500
assert transfer.source_stock_after >= transfer.source_safety_stock
assert round(transfer.protected_revenue) == 184_000
assert hero_sales_change(data) < -0.45
assert bad_distributor.distributor_name == "Al Noor Distribution"
assert bad_distributor.fill_rate == 0.84
assert promo.volume_lift > 0.30 and promo.margin_pct < promo.baseline_margin_pct and promo.roi < 0

print("All planted commercial stories validated.")
print(f"Jeddah shortage: {hero.shortage_units:,.0f} units")
print(f"Recommended transfer: {transfer.recommended_transfer:,.0f} units")
print(f"Protected revenue: SAR {transfer.protected_revenue:,.0f}")

