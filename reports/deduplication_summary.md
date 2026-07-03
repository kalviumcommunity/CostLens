# Deduplication Summary — LU-10

## Row Count Comparison

| Metric | Value |
| ------ | ----- |
| Rows before | 24 |
| Exact duplicates removed | 2 |
| Near duplicates removed | 2 |
| Total rows removed | 4 |
| Rows after | 20 |

## Deduplication Policy

- **Entity key (near-duplicates):** `Deployment_ID`
- **Exact duplicates:** detected with `df.duplicated(keep="first")`; the first occurrence is kept.
- **Near duplicates:** per entity, keep the **most complete** record (fewest nulls); ties broken by the most recent `Billing_Date`.
- **Audit trail:** every removed record is logged to `reports/removed_duplicates.csv` with its duplicate type and removal reason.

