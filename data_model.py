from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd


AS_OF_DATE = pd.Timestamp("2026-08-01")
HERO_PRODUCT = "Cola 330ml"


@dataclass(frozen=True)
class DemoData:
    products: pd.DataFrame
    distributors: pd.DataFrame
    sales: pd.DataFrame
    inventory: pd.DataFrame
    forecast: pd.DataFrame
    promotions: pd.DataFrame
    executive_kpis: pd.DataFrame
    regional_performance: pd.DataFrame
    distributor_performance: pd.DataFrame
    inventory_risk: pd.DataFrame
    transfer_recommendations: pd.DataFrame
    promotion_effectiveness: pd.DataFrame


def _products() -> pd.DataFrame:
    rows = [
        ("P001", HERO_PRODUCT, "Cola", "330ml", 184_000 / 8_500, 12.20),
        ("P002", "Cola 500ml", "Cola", "500ml", 27.00, 15.00),
        ("P003", "Lemon 330ml", "Citrus", "330ml", 20.00, 11.10),
        ("P004", "Orange 330ml", "Citrus", "330ml", 20.50, 11.30),
        ("P005", "Diet Cola 330ml", "Cola", "330ml", 22.00, 12.80),
    ]
    return pd.DataFrame(rows, columns=["product_id", "product_name", "category", "pack_size", "unit_price", "unit_cost"])


def _distributors() -> pd.DataFrame:
    rows = [
        ("D01", "Red Sea Trading", "West", "Jeddah", 8_000_000),
        ("D02", "Central Route Co.", "Central", "Riyadh", 9_200_000),
        ("D03", "Al Noor Distribution", "East", "Dammam", 6_800_000),
        ("D04", "Northern Markets", "North", "Tabuk", 4_500_000),
        ("D05", "Southern Supply", "South", "Abha", 4_200_000),
    ]
    return pd.DataFrame(rows, columns=["distributor_id", "distributor_name", "region", "city", "target_revenue"])


def _sales(products: pd.DataFrame, distributors: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(17)
    dates = pd.date_range("2026-02-01", "2026-07-31", freq="D")
    channels = ["Traditional Trade", "Modern Trade", "E-commerce", "Food Service"]
    rows: list[dict] = []
    order_no = 1
    for date in dates:
        seasonal = 1 + 0.09 * np.sin((date.dayofyear - 90) / 365 * 2 * np.pi)
        for d_idx, distributor in distributors.iterrows():
            for p_idx, product in products.iterrows():
                demand = (210 + 20 * p_idx + 14 * d_idx) * seasonal * rng.normal(1, 0.06)
                availability = 1.0
                if product.product_name == HERO_PRODUCT and distributor.city == "Jeddah" and date >= pd.Timestamp("2026-07-18"):
                    availability = 0.52 if date < pd.Timestamp("2026-07-25") else 0.30
                units = max(0, int(demand * availability))
                discount_rate = 0.04
                if product.product_name == "Cola 500ml" and distributor.city == "Riyadh" and date >= pd.Timestamp("2026-07-01"):
                    units = int(units * 1.42)
                    discount_rate = 0.33
                gross = units * product.unit_price
                discount = gross * discount_rate
                net = gross - discount
                cogs = units * product.unit_cost
                rows.append({
                    "sale_date": date,
                    "order_id": f"SO{order_no:07d}",
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "distributor_id": distributor.distributor_id,
                    "distributor_name": distributor.distributor_name,
                    "city": distributor.city,
                    "region": distributor.region,
                    "channel": channels[(date.day + p_idx + d_idx) % len(channels)],
                    "units_sold": units,
                    "gross_revenue": gross,
                    "discount_amount": discount,
                    "net_revenue": net,
                    "cogs": cogs,
                    "margin": net - cogs,
                    "estimated_demand": int(demand),
                })
                order_no += 1
    return pd.DataFrame(rows)


def _inventory(products: pd.DataFrame, distributors: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(23)
    dates = pd.date_range("2026-07-20", AS_OF_DATE, freq="D")
    hero_jeddah = [28_000, 25_000, 21_000, 17_000, 14_000, 11_000, 8_500, 6_500, 5_300, 5_000, 4_800, 4_650, 4_500]
    rows = []
    for date_idx, date in enumerate(dates):
        for _, distributor in distributors.iterrows():
            for _, product in products.iterrows():
                if product.product_name == HERO_PRODUCT and distributor.city == "Jeddah":
                    closing = hero_jeddah[date_idx]
                    safety = 10_000
                elif product.product_name == HERO_PRODUCT and distributor.city == "Riyadh":
                    closing = 40_000
                    safety = 15_000
                else:
                    closing = int(rng.integers(13_000, 31_000))
                    safety = 9_000
                rows.append({
                    "inventory_date": date,
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "city": distributor.city,
                    "warehouse": f"{distributor.city} DC",
                    "closing_stock": closing,
                    "safety_stock": safety,
                    "inventory_value": closing * product.unit_cost,
                })
    return pd.DataFrame(rows)


def _forecast(products: pd.DataFrame, distributors: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(31)
    dates = pd.date_range(AS_OF_DATE, periods=7, freq="D")
    rows = []
    for _, distributor in distributors.iterrows():
        for _, product in products.iterrows():
            if product.product_name == HERO_PRODUCT and distributor.city == "Jeddah":
                daily = [1850, 1850, 1850, 1850, 1850, 1850, 1900]
            else:
                daily = rng.integers(850, 1_550, size=7).tolist()
            for date, units in zip(dates, daily):
                rows.append({"forecast_date": date, "product_id": product.product_id, "product_name": product.product_name,
                             "city": distributor.city, "forecast_units": int(units), "model_version": "demo-v1"})
    return pd.DataFrame(rows)


def _promotions() -> pd.DataFrame:
    return pd.DataFrame([
        ("PR01", "Cola 500ml Riyadh Volume Push", "Cola 500ml", "Riyadh", "2026-07-01", "2026-07-31", 0.33),
        ("PR02", "Citrus Summer Bundle", "Lemon 330ml", "Jeddah", "2026-06-01", "2026-06-30", 0.08),
    ], columns=["promotion_id", "promotion_name", "product_name", "city", "start_date", "end_date", "discount_rate"])


def _gold_tables(products, distributors, sales, inventory, forecast, promotions):
    current = sales[sales.sale_date >= pd.Timestamp("2026-07-01")]
    prior = sales[(sales.sale_date >= pd.Timestamp("2026-06-01")) & (sales.sale_date < pd.Timestamp("2026-07-01"))]
    revenue = current.net_revenue.sum()
    prior_revenue = prior.net_revenue.sum()
    latest = inventory[inventory.inventory_date == inventory.inventory_date.max()]
    forecast_7d = forecast.groupby(["product_id", "product_name", "city"], as_index=False).forecast_units.sum()
    risk = forecast_7d.merge(latest[["product_id", "city", "closing_stock", "safety_stock", "inventory_value"]], on=["product_id", "city"])
    risk = risk.merge(products[["product_id", "unit_price"]], on="product_id")
    risk["shortage_units"] = (risk.forecast_units - risk.closing_stock).clip(lower=0)
    risk["days_of_cover"] = risk.closing_stock / (risk.forecast_units / 7)
    risk["risk_level"] = np.select([risk.shortage_units > 0, risk.closing_stock < risk.safety_stock], ["HIGH", "MEDIUM"], default="LOW")
    risk["revenue_at_risk"] = risk.shortage_units * risk.unit_price

    hero = risk[(risk.product_name == HERO_PRODUCT) & (risk.city == "Jeddah")].iloc[0]
    source = risk[(risk.product_name == HERO_PRODUCT) & (risk.city == "Riyadh")].iloc[0]
    transfer = min(int(hero.shortage_units), int(source.closing_stock - source.safety_stock))
    transfers = pd.DataFrame([{
        "product_name": HERO_PRODUCT, "source_city": "Riyadh", "destination_city": "Jeddah",
        "recommended_transfer": transfer, "source_stock_before": int(source.closing_stock),
        "source_stock_after": int(source.closing_stock - transfer), "source_safety_stock": int(source.safety_stock),
        "protected_revenue": transfer * float(hero.unit_price),
    }])

    regional = current.groupby(["region", "city"], as_index=False).agg(revenue=("net_revenue", "sum"), margin=("margin", "sum"))
    prior_reg = prior.groupby("region", as_index=False).net_revenue.sum().rename(columns={"net_revenue": "prior_revenue"})
    regional = regional.merge(prior_reg, on="region")
    regional["growth"] = regional.revenue / regional.prior_revenue - 1
    regional["margin_pct"] = regional.margin / regional.revenue

    distributor_perf = current.groupby(["distributor_id", "distributor_name", "city"], as_index=False).agg(revenue=("net_revenue", "sum"), margin=("margin", "sum"))
    prior_dist = prior.groupby("distributor_id", as_index=False).net_revenue.sum().rename(columns={"net_revenue": "prior_revenue"})
    distributor_perf = distributor_perf.merge(prior_dist, on="distributor_id")
    distributor_perf["growth"] = distributor_perf.revenue / distributor_perf.prior_revenue - 1
    distributor_perf["margin_pct"] = distributor_perf.margin / distributor_perf.revenue
    distributor_perf["fill_rate"] = [0.96, 0.95, 0.84, 0.93, 0.94]
    distributor_perf["return_rate"] = [0.018, 0.021, 0.060, 0.027, 0.025]
    distributor_perf["stock_outs"] = [9, 2, 12, 4, 3]
    distributor_perf["score"] = [82, 88, 62, 79, 81]

    promo_sales = current[(current.product_name == "Cola 500ml") & (current.city == "Riyadh")]
    baseline = prior[(prior.product_name == "Cola 500ml") & (prior.city == "Riyadh")]
    promotion_effectiveness = pd.DataFrame([{
        "promotion_name": "Cola 500ml Riyadh Volume Push", "city": "Riyadh",
        "volume_lift": promo_sales.units_sold.sum() / baseline.units_sold.sum() - 1,
        "margin_pct": promo_sales.margin.sum() / promo_sales.net_revenue.sum(),
        "baseline_margin_pct": baseline.margin.sum() / baseline.net_revenue.sum(),
        "roi": -0.18,
    }])

    executive = pd.DataFrame([{
        "revenue": revenue, "revenue_growth": revenue / prior_revenue - 1,
        "margin_pct": current.margin.sum() / revenue, "target_attainment": 0.96,
        "inventory_value": latest.inventory_value.sum(), "at_risk_skus": int((risk.risk_level == "HIGH").sum()),
        "forecast_accuracy": 0.87, "promotion_roi": 1.8, "revenue_at_risk": risk.revenue_at_risk.sum(),
    }])
    return executive, regional, distributor_perf, risk.sort_values("revenue_at_risk", ascending=False), transfers, promotion_effectiveness


@lru_cache(maxsize=1)
def build_demo_data() -> DemoData:
    products = _products()
    distributors = _distributors()
    sales = _sales(products, distributors)
    inventory = _inventory(products, distributors)
    forecast = _forecast(products, distributors)
    promotions = _promotions()
    gold = _gold_tables(products, distributors, sales, inventory, forecast, promotions)
    return DemoData(products, distributors, sales, inventory, forecast, promotions, *gold)

