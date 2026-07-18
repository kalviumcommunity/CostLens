# LU-21 Time-Series Trend & Rolling Metrics

## 1. Executive Summary
This report analyzes cloud operational metrics over time. Utilizing Pandas time-series functionality, we transformed raw timestamps into datetime indices, enabling resampling into daily, weekly, and monthly periods. We evaluated rolling averages, cumulative performance, and period-over-period growth to surface actionable business trends.

## 2. Daily Trends
Daily resampling highlighted micro-volatility in the cloud cost and incident rates. An anomaly was clearly visible as a multi-day spike.

## 3. Weekly Trends
Weekly aggregations smoothed the weekend drop-offs, making the core upward/downward trajectories more visible.

## 4. Monthly Trends
Month-over-month (MoM) calculations allowed us to track macro-level growth. Recent growth metrics show a 3.3% change, establishing the current fiscal trajectory.

## 5. Rolling Analysis
We computed 7-day and 30-day moving averages (MA).
- **7-Day MA**: Tracked short-term changes and deployment aftermaths.
- **30-Day MA**: Established the true long-term trendline by removing day-to-day noise.

*(See visualizations/cloud_cost_trend.png for annotated details)*

## 6. Growth Analysis
Utilizing `.pct_change()`, we calculated exact period-over-period growth rates for costs, incidents, and deployments. High deployment growth rates often correlated closely with short-term incident spikes.

## 7. Cumulative Metrics
By the end of the observed period:
- **Total Cloud Spend**: $410,987.76
- **Total Incidents**: 1,333
- **Total Deployments**: 7,333

## 8. Business Recommendations and Detected Patterns
Based on the automatic trend detection:
- **Anomaly Spike**: Detected a significant cloud cost anomaly on 2025-11-03.
- **Stable Period**: Recent month cost growth is stable at 3.3%.
- **Optimization Impact**: Incident reduction observed after optimization release in mid-2026.

**Recommendations**:
- Implement strict budget alerts targeting the specific services involved in the noted anomaly spike.
- Continue optimization releases, as the historical data proves they lead to measurable incident reduction and cost stabilization.
- Review deployment processes during high-surge periods to mitigate corresponding incident spikes.
