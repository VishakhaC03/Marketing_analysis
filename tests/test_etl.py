import pandas as pd
import pytest
from etl import transform

def sample():
    c = pd.DataFrame([{"campaign_id":1,"campaign_name":"Test","channel":"Email","budget":100}])
    p = pd.DataFrame([{"campaign_id":1,"date":"2026-01-01","impressions":100,
                       "clicks":10,"conversions":2,"spend":5}])
    return c,p

def test_rates():
    c,p = transform(*sample())
    assert p.loc[0,"ctr_pct"] == 10
    assert p.loc[0,"conversion_rate_pct"] == 20
    assert p.loc[0,"cpc"] == .5

def test_bad_clicks():
    c,p = sample()
    p.loc[0,"clicks"] = 101
    with pytest.raises(ValueError, match="Clicks exceed"):
        transform(c,p)

def test_unknown_campaign():
    c,p = sample()
    p.loc[0,"campaign_id"] = 999
    with pytest.raises(ValueError, match="Unknown"):
        transform(c,p)

def test_duplicate_day():
    c,p = sample()
    with pytest.raises(ValueError, match="Duplicate"):
        transform(c,pd.concat([p,p], ignore_index=True))

def test_missing_column():
    c,p = sample()
    with pytest.raises(ValueError, match="missing columns"):
        transform(c,p.drop(columns=["spend"]))
