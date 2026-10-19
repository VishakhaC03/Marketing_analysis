"""Interactive Streamlit dashboard backed by the transformed SQL tables."""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Marketing Campaign Analytics", layout="wide")
st.title("Marketing Campaign Analytics Dashboard")
url = os.getenv("DATABASE_URL", "sqlite:///marketing_analytics.db")
try:
    engine = create_engine(url)
    with engine.connect() as connection:
        df = pd.read_sql("""
            SELECT c.campaign_name, c.channel, p.date, p.impressions, p.clicks,
                   p.conversions, p.spend
            FROM performance p JOIN campaigns c ON p.campaign_id = c.campaign_id
        """, connection)
    engine.dispose()
except Exception as exc:
    st.error("Database unavailable. Run `python generate_data.py` and `python etl.py` first.")
    st.stop()
df["date"] = pd.to_datetime(df["date"])
channels = st.multiselect("Channel", sorted(df["channel"].unique()), default=sorted(df["channel"].unique()))
filtered = df[df["channel"].isin(channels)]
if filtered.empty:
    st.info("Select at least one channel.")
    st.stop()
impressions = int(filtered["impressions"].sum())
clicks = int(filtered["clicks"].sum())
conversions = int(filtered["conversions"].sum())
spend = float(filtered["spend"].sum())
metrics = st.columns(5)
for col, label, value in zip(metrics,
    ["Impressions","Clicks","Conversions","Spend","CTR"],
    [f"{impressions:,}",f"{clicks:,}",f"{conversions:,}",f"${spend:,.2f}",
     f"{100*clicks/impressions if impressions else 0:.2f}%"]):
    col.metric(label, value)
st.caption(f"Conversion rate: {100*conversions/clicks if clicks else 0:.2f}% | "
           f"Cost per conversion: ${spend/conversions if conversions else 0:.2f}")
daily = filtered.groupby("date", as_index=False)[["impressions","clicks","conversions","spend"]].sum()
st.plotly_chart(px.line(daily, x="date", y="spend", title="Daily Spend"), use_container_width=True)
by_campaign = filtered.groupby(["campaign_name","channel"], as_index=False)[
    ["impressions","clicks","conversions","spend"]].sum()
by_campaign["ctr_pct"] = (100*by_campaign["clicks"] /
                          by_campaign["impressions"].replace(0,float("nan"))).fillna(0).round(2)
by_campaign["conversion_rate_pct"] = (100*by_campaign["conversions"] /
                          by_campaign["clicks"].replace(0,float("nan"))).fillna(0).round(2)
st.plotly_chart(px.bar(by_campaign, x="campaign_name", y="conversions", color="channel",
                       title="Conversions by Campaign"), use_container_width=True)
st.subheader("Campaign Performance")
st.dataframe(by_campaign, use_container_width=True)
