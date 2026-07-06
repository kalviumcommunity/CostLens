"""
LU-13 :: Outlier Detection with Statistical Methods
====================================================

Applies Z-score and Interquartile Range (IQR) methods to detect numerical outliers
in the cloud cost dataset. Decisions (cap, remove, flag) are explicitly chosen per
column based on business context, and all transformations are logged.

Inputs:
    - data/processed/cloud_cost_dataset_datetime_features.csv
Outputs:
    - data/processed/cloud_cost_dataset_outliers.csv
    - reports/outlier_cleaning_log.md
    - reports/outlier_detection_summary.csv

Run:
    python scripts/outlier_detection.py
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Configuration: input (read-only) and output targets.
# ---------------------------------------------------------------------------
INPUT_FILE = os.path.join("data", "processed", "cloud_cost_dataset_datetime_features.csv")
OUTPUT_FILE = os.path.join("data", "processed", "cloud_cost_dataset_outliers.csv")
REPORTS_DIR = "reports"
CLEANING_LOG_MD = os.path.join(REPORTS_DIR, "outlier_cleaning_log.md")
SUMMARY_CSV = os.path.join(REPORTS_DIR, "outlier_detection_summary.csv")

# Z-score threshold for outlier detection (standard is 3.0, but we can configure it)
Z_SCORE_THRESHOLD = 3.0


# ---------------------------------------------------------------------------
# load_dataset(): read the enriched CSV.
# ---------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load the dataset with datetime features."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Processed dataset not found at '{path}'. Please run previous scripts first.")
    return pd.read_csv(path, encoding="utf-8")


# ---------------------------------------------------------------------------
# detect_outliers_zscore(): detect outliers using Z-score method.
# ---------------------------------------------------------------------------
def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Returns a boolean mask of outliers using the Z-score method."""
    # Convert series to numeric, coerce errors, fill missing with mean
    numeric_series = pd.to_numeric(series, errors='coerce')
    mean = numeric_series.mean()
    std = numeric_series.std()
    if std == 0 or pd.isna(std):
        return pd.Series(False, index=series.index)
    
    z_scores = (numeric_series - mean) / std
    return z_scores.abs() > threshold


# ---------------------------------------------------------------------------
# detect_outliers_iqr(): detect outliers using Interquartile Range method.
# ---------------------------------------------------------------------------
def detect_outliers_iqr(series: pd.Series) -> tuple[pd.Series, float, float]:
    """Returns a boolean mask of outliers using IQR, plus lower/upper bounds."""
    numeric_series = pd.to_numeric(series, errors='coerce')
    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    mask = (numeric_series < lower_bound) | (numeric_series > upper_bound)
    return mask, lower_bound, upper_bound


def main() -> None:
    # Ensure directories exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 1. Load dataset
    df = load_dataset(INPUT_FILE)
    print("=" * 60)
    print("LU-13 OUTLIER DETECTION")
    print("=" * 60)
    print(f"Loaded dataset: {INPUT_FILE} ({len(df)} rows)")

    # 2. Identify target numerical columns
    # We support either CPU_Usage or CPU_Utilization, along with Monthly_Cost
    numeric_cols = []
    for col in ["Monthly_Cost", "CPU_Usage", "CPU_Utilization"]:
        if col in df.columns:
            # Check if it has numeric values or can be cast
            try:
                pd.to_numeric(df[col], errors='coerce')
                numeric_cols.append(col)
            except Exception:
                pass

    print(f"Target numerical columns identified: {numeric_cols}\n")

    # 3. Detect and Handle Outliers
    out = df.copy()
    summary_records = []
    log_decisions = []

    for col in numeric_cols:
        series = pd.to_numeric(out[col], errors='coerce')
        
        # A. Detect using Z-score
        z_mask = detect_outliers_zscore(series, Z_SCORE_THRESHOLD)
        z_count = int(z_mask.sum())
        
        # B. Detect using IQR
        iqr_mask, lower_bound, upper_bound = detect_outliers_iqr(series)
        iqr_count = int(iqr_mask.sum())
        
        # Combine masks for overall detection profile
        any_outlier_mask = z_mask | iqr_mask
        any_count = int(any_outlier_mask.sum())
        
        summary_records.append({
            "Column": col,
            "Total_Rows": len(df),
            "Z_Score_Outliers": z_count,
            "IQR_Outliers": iqr_count,
            "Combined_Outliers": any_count,
            "IQR_Lower_Bound": round(lower_bound, 2),
            "IQR_Upper_Bound": round(upper_bound, 2),
        })

        # C. Decide handling action per column
        if col == "Monthly_Cost":
            # Decision: FLAG outliers (add binary column)
            # Justification: Financial spikes reflect real spend events that finance
            # must reconcile, so capping or deleting them would falsify invoice reporting.
            flag_col = f"{col}_outlier_flag"
            out[flag_col] = any_outlier_mask.astype(int)
            action = "Flagged"
            details = f"Added binary flag column '{flag_col}'"
            reason = "Financial spikes reflect real spend events that finance must reconcile; capping/removing them would distort actual balance sheets."
        
        elif col in ["CPU_Usage", "CPU_Utilization"]:
            # Decision: CAP outliers to IQR bounds (Winsorize)
            # Justification: Extreme transient performance peaks skew baseline utilization statistics
            # and capacity planning models, so capping them to normal boundaries stabilizes metrics.
            # We also add a flag to preserve traceability of where capping occurred.
            flag_col = f"{col}_outlier_flag"
            out[flag_col] = any_outlier_mask.astype(int)
            
            # Apply capping
            out[col] = series.clip(lower=lower_bound, upper=upper_bound)
            action = "Capped"
            details = f"Capped values outside [{round(lower_bound, 2)}, {round(upper_bound, 2)}] to boundaries. Added flag '{flag_col}'"
            reason = "Extreme transient utilization peaks skew capacity planning; capping stabilizes baseline analysis while flags preserve audit capability."
        
        else:
            # Default fallback: flag
            flag_col = f"{col}_outlier_flag"
            out[flag_col] = any_outlier_mask.astype(int)
            action = "Flagged"
            details = f"Added binary flag column '{flag_col}'"
            reason = "Flagged for manual review."

        log_decisions.append({
            "column": col,
            "action": action,
            "z_detected": z_count,
            "iqr_detected": iqr_count,
            "bounds": f"[{round(lower_bound, 2)}, {round(upper_bound, 2)}]",
            "details": details,
            "reason": reason
        })

    # 4. Save structured summary CSV
    summary_df = pd.DataFrame(summary_records)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    print("=" * 60)
    print("OUTLIER DETECTION SUMMARY")
    print("=" * 60)
    print(summary_df.to_string(index=False))
    print()

    # 5. Write Cleaning Log Markdown
    log_lines = [
        "# Outlier Handling Decisions & Cleaning Log — LU-13\n",
        "This cleaning log documents the statistical methods used to identify outliers and the ",
        "business-aware handling decisions applied to each numerical column in the dataset.\n",
        "## Summary table\n",
        "| Column | Outliers (IQR / Z) | Action Taken | Bounds Used | Justification |",
        "| ------ | ------------------ | ------------ | ----------- | ------------- |"
    ]
    for d in log_decisions:
        log_lines.append(
            f"| {d['column']} | {d['iqr_detected']} / {d['z_detected']} | {d['action']} | `{d['bounds']}` | {d['reason']} |"
        )
    log_lines.append("\n## Detailed Action Logs\n")
    for d in log_decisions:
        log_lines.append(f"### `{d['column']}`")
        log_lines.append(f"- **Detection Methods:** Z-Score ($|Z| > {Z_SCORE_THRESHOLD}$) and Interquartile Range (IQR $1.5\\times$ Rule)")
        log_lines.append(f"- **Outliers Detected:** {d['iqr_detected']} by IQR, {d['z_detected']} by Z-score")
        log_lines.append(f"- **Action Taken:** {d['action']}")
        log_lines.append(f"- **Details:** {d['details']}")
        log_lines.append(f"- **Business Rationale:** {d['reason']}\n")

    with open(CLEANING_LOG_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines) + "\n")

    # 6. Save modified dataset separately
    out.to_csv(OUTPUT_FILE, index=False)
    print("Generated:")
    print(f"  {SUMMARY_CSV}")
    print(f"  {CLEANING_LOG_MD}")
    print(f"  {OUTPUT_FILE}")
    print(f"\nSource dataset untouched: {INPUT_FILE}")


if __name__ == "__main__":
    main()
