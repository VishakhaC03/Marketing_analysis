"""Create reproducible synthetic marketing campaign data (no personal data)."""
from pathlib import Path
import random
import pandas as pd

RAW = Path("data/raw")
def main():
    RAW.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    campaigns = [
        (1, "Search - Awareness", "Google Ads", 3500),
        (2, "Social - Autumn", "Meta Ads", 2900),
        (3, "Email - Welcome", "Email", 800),
        (4, "Search - Retargeting", "Google Ads", 2200),
        (5, "Social - Loyalty", "Meta Ads", 1800),
    ]
    pd.DataFrame(campaigns, columns=["campaign_id","campaign_name","channel","budget"]).to_csv(
        RAW / "campaigns.csv", index=False)
    rows = []
    for campaign_id, _, channel, _ in campaigns:
        for day in pd.date_range("2026-01-01", periods=60):
            impressions = rng.randint(500, 5000)
            clicks = rng.randint(20, min(impressions, 450))
            conversions = rng.randint(0, clicks)
            spend = round(rng.uniform(15, 90), 2)
            rows.append([campaign_id, day.date().isoformat(), impressions, clicks, conversions, spend])
    pd.DataFrame(rows, columns=["campaign_id","date","impressions","clicks","conversions","spend"]).to_csv(
        RAW / "performance.csv", index=False)
    print("Generated 5 campaigns and 300 daily performance rows in data/raw/")

if __name__ == "__main__":
    main()
