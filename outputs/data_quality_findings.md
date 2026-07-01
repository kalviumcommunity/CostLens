# Data Quality Findings

## Issue 1
Missing values found in: cost_usd

**Proposed Fix:**
Median imputation for numeric, mode/flag for categorical

## Issue 2
Duplicate rows detected in the dataset

**Proposed Fix:**
Deduplication using df.drop_duplicates()

## Issue 3
Duplicate deployment records detected (14 repeated deployment_id values)

**Proposed Fix:**
Aggregate or deduplicate using deployment_id

## Issue 4
Inconsistent category labels in 'environment' (case/whitespace variants)

**Proposed Fix:**
Category standardisation (strip + normalise case)

## Issue 5
Suspicious outliers detected in 'cost_usd' (1 values outside IQR bounds)

**Proposed Fix:**
Review outliers; cap/winsorise or flag for RCA
