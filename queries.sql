-- Run against the database after ETL. Rates use aggregate totals, not averages of daily rates.
SELECT c.campaign_name, c.channel,
       SUM(p.impressions) AS impressions,
       SUM(p.clicks) AS clicks,
       SUM(p.conversions) AS conversions,
       ROUND(SUM(p.spend), 2) AS spend,
       ROUND(100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0), 2) AS ctr_pct,
       ROUND(100.0 * SUM(p.conversions) / NULLIF(SUM(p.clicks), 0), 2) AS conversion_rate_pct,
       ROUND(SUM(p.spend) / NULLIF(SUM(p.conversions), 0), 2) AS cost_per_conversion
FROM performance p
JOIN campaigns c ON c.campaign_id = p.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.channel
ORDER BY conversions DESC;

-- Daily campaign totals
SELECT date, SUM(impressions) AS impressions, SUM(clicks) AS clicks,
       SUM(conversions) AS conversions, ROUND(SUM(spend), 2) AS spend
FROM performance GROUP BY date ORDER BY date;
