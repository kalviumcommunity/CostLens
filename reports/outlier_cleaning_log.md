# Outlier Handling Decisions & Cleaning Log — LU-13

This cleaning log documents the statistical methods used to identify outliers and the 
business-aware handling decisions applied to each numerical column in the dataset.

## Summary table

| Column | Outliers (IQR / Z) | Action Taken | Bounds Used | Justification |
| ------ | ------------------ | ------------ | ----------- | ------------- |
| Monthly_Cost | 0 / 0 | Flagged | `[-731.26, 2086.34]` | Financial spikes reflect real spend events that finance must reconcile; capping/removing them would distort actual balance sheets. |
| CPU_Usage | 0 / 0 | Capped | `[-18.76, 140.14]` | Extreme transient utilization peaks skew capacity planning; capping stabilizes baseline analysis while flags preserve audit capability. |

## Detailed Action Logs

### `Monthly_Cost`
- **Detection Methods:** Z-Score ($|Z| > 3.0$) and Interquartile Range (IQR $1.5\times$ Rule)
- **Outliers Detected:** 0 by IQR, 0 by Z-score
- **Action Taken:** Flagged
- **Details:** Added binary flag column 'Monthly_Cost_outlier_flag'
- **Business Rationale:** Financial spikes reflect real spend events that finance must reconcile; capping/removing them would distort actual balance sheets.

### `CPU_Usage`
- **Detection Methods:** Z-Score ($|Z| > 3.0$) and Interquartile Range (IQR $1.5\times$ Rule)
- **Outliers Detected:** 0 by IQR, 0 by Z-score
- **Action Taken:** Capped
- **Details:** Capped values outside [-18.76, 140.14] to boundaries. Added flag 'CPU_Usage_outlier_flag'
- **Business Rationale:** Extreme transient utilization peaks skew capacity planning; capping stabilizes baseline analysis while flags preserve audit capability.

