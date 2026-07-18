# LU-25: Anomaly Detection & Risk Identification

## 1. Executive Summary
This report identifies statistical and business-logic anomalies across our cloud operations. Utilizing three discrete detection algorithms (Hard Thresholds, Interquartile Range, and Rolling Z-Scores), we have isolated events that breach acceptable operational constraints.

- **Total Anomalies Detected**: 10
- **Critical Anomalies**: 0

## 2. Detected Anomalies
Below is a sample of the most severe anomalies detected across the monitored metrics:

| timestamp   | metric_name                |    value | severity   | detection_method   |
|:------------|:---------------------------|---------:|:-----------|:-------------------|
| 2026-02-19  | service_cost               | 600      | HIGH       | Threshold (> 500)  |
| 2026-04-15  | service_cost               | 750      | HIGH       | Threshold (> 500)  |
| 2026-05-18  | resource_utilization_score |  81.9587 | HIGH       | IQR Bound          |
| 2026-06-19  | service_cost               | 520      | HIGH       | Threshold (> 500)  |
| 2026-07-18  | service_cost               | 408.807  | HIGH       | IQR Bound          |
| 2026-03-01  | resource_utilization_score |  25      | MEDIUM     | Threshold (< 40)   |
| 2026-04-12  | resource_utilization_score |  35.9565 | MEDIUM     | Threshold (< 40)   |
| 2026-04-30  | resource_utilization_score |  30      | MEDIUM     | Threshold (< 40)   |
| 2026-01-30  | deployment_count           |  18      | LOW        | Threshold (> 15)   |
| 2026-05-20  | deployment_count           |  20      | LOW        | Threshold (> 15)   |

## 3. Business Impact
Left unchecked, these anomalies represent direct risks to the organization:
- **Service Cost Spikes**: A single uncontrolled spike (e.g., $750/day vs $300 avg) rapidly depletes operational budgets and nullifies reserved instance planning.
- **Utilization Drops**: Plunging utilization scores indicate ghost infrastructure—we are paying for machines that are completely idle.
- **Deployment Surges**: Extreme outliers in daily deployment counts heavily correlate with subsequent incident spikes and SLA breaches.

## 4. Potential Causes
Based on the detected metrics, potential root causes include:
- **Cost**: Abandoned test environments or auto-scaling groups stuck at maximum bounds.
- **Utilization**: Service outages routing traffic away from active clusters, or extreme over-provisioning during peak estimation.
- **Deployments**: CI/CD automation loops retrying failed builds uncontrollably.

## 5. Recommended Actions
1. **Immediate Review**: Investigate the CRITICAL severity spikes in `service_cost` immediately via AWS Cost Explorer.
2. **Alert Integration**: Connect the rolling Z-Score algorithm to Slack/PagerDuty to alert FinOps the moment a metric breaks its 7-day trend line.
3. **Rightsizing**: Review instances flagged by the low utilization threshold and downsize them to match actual memory/CPU demand.

*(See visualizations/anomaly_dashboard.png for graphical mapping)*
