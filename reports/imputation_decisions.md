# Imputation Decisions — LU-08

Every column with missing values and the business-aware strategy used to resolve it. The raw dataset is preserved; imputation is applied only to the cleaned copy.

| Column | Missing % | Method Used | Reason |
| ------ | --------- | ----------- | ------ |
| Monthly_Cost | 10.0% | Median | Numeric spend column; median is less sensitive to outliers than the mean, so extreme bills do not skew the fill value. |
| CPU_Usage | 20.0% | Median | Numeric utilisation metric; median preserves the central tendency without being distorted by spiky workloads. |
| Team_Name | 15.0% | Mode | Categorical owner; the most frequent team is the safest default and keeps the category distribution realistic. |
| Environment | 10.0% | Mode | Categorical lifecycle stage with few values; mode assigns the most common environment as a sensible default. |
| Deployment_Date | 15.0% | Forward Fill | Time-series column ordered by deployment; forward fill carries the last known date forward to keep chronology. |
| Cost_Center | 20.0% | Constant "Unknown" | Business rule: a missing cost center cannot be guessed, so it is explicitly flagged as 'Unknown' for finance review. |
