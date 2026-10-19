"""Extract CSVs, validate, transform, and load campaign analytics into SQL."""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

RAW = Path("data/raw")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///marketing_analytics.db")
PERFORMANCE_COLS = ["campaign_id","date","impressions","clicks","conversions","spend"]
CAMPAIGN_COLS = ["campaign_id","campaign_name","channel","budget"]

def extract(raw=RAW):
    return (pd.read_csv(raw / "campaigns.csv"), pd.read_csv(raw / "performance.csv"))

def transform(campaigns, performance):
    for label, frame, cols in [
        ("campaigns", campaigns, CAMPAIGN_COLS),
        ("performance", performance, PERFORMANCE_COLS),
    ]:
        missing = set(cols) - set(frame.columns)
        if missing:
            raise ValueError(f"{label}: missing columns {sorted(missing)}")
        if frame[cols].isna().any().any():
            raise ValueError(f"{label}: null values in required columns")
    campaigns = campaigns[CAMPAIGN_COLS].copy()
    performance = performance[PERFORMANCE_COLS].copy()
    if campaigns["campaign_id"].duplicated().any():
        raise ValueError("Duplicate campaign IDs")
    if performance.duplicated(["campaign_id","date"]).any():
        raise ValueError("Duplicate campaign/date rows")
    for col in ["campaign_id","budget"]:
        campaigns[col] = pd.to_numeric(campaigns[col], errors="raise")
    for col in ["campaign_id","impressions","clicks","conversions","spend"]:
        performance[col] = pd.to_numeric(performance[col], errors="raise")
    performance["date"] = pd.to_datetime(performance["date"], errors="raise").dt.date
    if campaigns["campaign_id"].isna().any() or performance["campaign_id"].isna().any():
        raise ValueError("Null campaign IDs after conversion")
    if (campaigns["budget"] < 0).any():
        raise ValueError("Negative budget")
    if (performance[["impressions","clicks","conversions","spend"]] < 0).any().any():
        raise ValueError("Negative performance values")
    if (performance["clicks"] > performance["impressions"]).any():
        raise ValueError("Clicks exceed impressions")
    if (performance["conversions"] > performance["clicks"]).any():
        raise ValueError("Conversions exceed clicks")
    if not performance["campaign_id"].isin(campaigns["campaign_id"]).all():
        raise ValueError("Unknown campaign ID in performance")
    if (campaigns["campaign_name"].astype(str).str.strip() == "").any():
        raise ValueError("Blank campaign name")
    if (campaigns["channel"].astype(str).str.strip() == "").any():
        raise ValueError("Blank channel")
    performance["ctr_pct"] = (100 * performance["clicks"] /
                              performance["impressions"].replace(0, float("nan"))).fillna(0).round(2)
    performance["conversion_rate_pct"] = (100 * performance["conversions"] /
                              performance["clicks"].replace(0, float("nan"))).fillna(0).round(2)
    performance["cpc"] = (performance["spend"] /
                              performance["clicks"].replace(0, float("nan"))).fillna(0).round(2)
    return campaigns, performance

def load(campaigns, performance, url=DB_URL):
    engine = create_engine(url)
    # This is a full-refresh demo: replacing both tables makes reruns idempotent.
    # A production system should use staging tables and transactional upserts.
    with engine.begin() as connection:
        campaigns.to_sql("campaigns", connection, if_exists="replace", index=False)
        performance.to_sql("performance", connection, if_exists="replace", index=False)
    engine.dispose()

def main():
    campaigns, performance = transform(*extract())
    load(campaigns, performance)
    print(f"ETL completed: {len(campaigns)} campaigns, {len(performance)} performance records.")
    print(f"Database: {DB_URL.split('@')[-1] if '@' in DB_URL else DB_URL}")

if __name__ == "__main__":
    main()
