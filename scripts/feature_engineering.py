"""
LU-16 :: Feature Engineering & Derived Business Columns
=========================================================

Engineers derived features carrying business meaning (recency, spending tiers,
risk index, and cost-to-risk ratio) from the conformed dataset.
Logic is written in modular, reusable functions and validated against expected
value ranges and edge cases.

Inputs:
    - data/processed/final_merged_dataset.csv
Outputs:
    - data/processed/final_merged_dataset_features.csv
    - reports/feature_engineering_summary.csv

Run:
    python scripts/feature_engineering.py
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
INPUT_FILE = os.path.join("data", "processed", "final_merged_dataset.csv")
OUTPUT_FILE = os.path.join("data", "processed", "final_merged_dataset_features.csv")
REPORTS_DIR = "reports"
SUMMARY_CSV = os.path.join(REPORTS_DIR, "feature_engineering_summary.csv")

# Reference date for deployment recency calculations
REFERENCE_DATE = "2026-02-01"


# ===========================================================================
# Reusable Feature Engineering Functions
# ===========================================================================

def calculate_deployment_recency(df: pd.DataFrame, date_col: str = "Deployment_Date", 
                                ref_date: str = REFERENCE_DATE) -> pd.Series:
    """Calculate the number of days elapsed between deployment date and the reference analysis date.
    
    If deployment date is missing (NaN/NaT), returns NaN to prevent skewing average recency.
    """
    ref_ts = pd.to_datetime(ref_date)
    dates = pd.to_datetime(df[date_col], errors="coerce")
    
    # Days since deployment
    delta = (ref_ts - dates).dt.days
    return delta


def segment_recency_tier(df: pd.DataFrame, recency_col: str = "Deployment_Recency_Days") -> pd.Series:
    """Bin the deployment recency days into standard business tiers.
    
    Tiers:
      - <= 15 days: 'Recent' (frequently modified, active lifecycle)
      - 16 - 30 days: 'Standard' (normal lifecycle duration)
      - > 30 days: 'Stale' (has not been deployed/refreshed recently)
    """
    # Use pd.cut for custom defined intervals
    bins = [-float('inf'), 15, 30, float('inf')]
    labels = ["Recent", "Standard", "Stale"]
    
    return pd.cut(df[recency_col], bins=bins, labels=labels)


def segment_spend_tier(df: pd.DataFrame, cost_col: str = "Monthly_Cost") -> pd.Series:
    """Bin monthly cost into equal-frequency tiers using pd.qcut.
    
    Tiers: Low Spend, Medium Spend, High Spend.
    If there are duplicate bin boundaries (common in small or synthetic datasets), 
    we fall back to a pd.cut with explicit thresholds.
    """
    labels = ["Low Spend", "Medium Spend", "High Spend"]
    try:
        # q=3 segments the data into 3 quantiles containing equal number of samples
        return pd.qcut(df[cost_col], q=3, labels=labels, duplicates="drop")
    except ValueError:
        # Fallback to pd.cut with logical default limits if quantiles overlap
        # Limits: Low: < 200, Medium: 200-800, High: > 800
        print("  [Warning] Quantiles overlap in qcut due to duplicates; falling back to pd.cut.")
        bins = [-float('inf'), 200, 800, float('inf')]
        return pd.cut(df[cost_col], bins=bins, labels=labels)


def derive_incident_severity_weight(df: pd.DataFrame, severity_col: str = "Severity") -> pd.Series:
    """Map categorical incident severity to numeric risk weight.
    
    Critical severity incidents carry more risk weight than Low severity ones.
    Missing/None values are mapped to 0 (no known risk).
    """
    severity_mapping = {
        "Critical": 5.0,
        "High": 3.0,
        "Medium": 2.0,
        "Low": 1.0
    }
    # Fill missing values with 0.0 weight
    return df[severity_col].map(severity_mapping).fillna(0.0)


def compute_cost_risk_score(df: pd.DataFrame, cost_col: str = "Monthly_Cost", 
                            severity_col: str = "Severity") -> tuple[pd.Series, pd.Series]:
    """Compute composite and ratio metrics to represent cost and operational stability together.
    
    Metrics:
      1. Cost_Risk_Index (Composite Score): Monthly_Cost * (1.0 + Severity_Weight)
         Combines resource cost with the severity weight of incidents it suffered.
         High index identifies expensive resources that are also highly unstable.
      2. Cost_per_Risk_Unit (Ratio Metric): Monthly_Cost / (1.0 + Severity_Weight)
         Measures financial efficiency. High ratio means high spending relative to stability risk.
    """
    severity_weight = derive_incident_severity_weight(df, severity_col)
    
    # Calculate composite index
    cost_risk_index = df[cost_col] * (1.0 + severity_weight)
    
    # Calculate ratio metric
    cost_per_risk_unit = df[cost_col] / (1.0 + severity_weight)
    
    return cost_risk_index, cost_per_risk_unit


# ===========================================================================
# Validation Logic
# ===========================================================================

def validate_features(df: pd.DataFrame) -> None:
    """Validate all engineered features against expected business bounds and ranges.
    
    Raises:
        ValueError: if any validation rule is violated.
    """
    print("\nValidating engineered features...")
    
    # 1. Recency range check (days since deployment cannot be negative)
    neg_recency = df["Deployment_Recency_Days"] < 0
    if neg_recency.any():
        offenders = df.loc[neg_recency, ["Project_ID", "Deployment_Recency_Days"]]
        raise ValueError(f"Recency check failed: Negative days found:\n{offenders}")
    print("  - Recency range: OK (all values >= 0 or NaN)")
    
    # 2. Risk index range check (must be >= 0)
    neg_risk = df["Cost_Risk_Index"] < 0
    if neg_risk.any():
        offenders = df.loc[neg_risk, ["Project_ID", "Cost_Risk_Index"]]
        raise ValueError(f"Risk index validation failed: Negative risk index found:\n{offenders}")
    print("  - Cost Risk Index: OK (all values >= 0)")

    # 3. Spend tier alignment check (High Spend must have higher average cost than Low Spend)
    low_spend_avg = df.loc[df["Spend_Tier"] == "Low Spend", "Monthly_Cost"].mean()
    high_spend_avg = df.loc[df["Spend_Tier"] == "High Spend", "Monthly_Cost"].mean()
    if pd.notna(low_spend_avg) and pd.notna(high_spend_avg) and low_spend_avg >= high_spend_avg:
        raise ValueError(f"Spend tier check failed: Low Spend average ({low_spend_avg}) "
                         f"is >= High Spend average ({high_spend_avg})")
    print("  - Spend Tiers: OK (High Spend average > Low Spend average)")
    
    # 4. Null value checks on binned categories (where input numerical data is valid)
    unbinned_costs = df[df["Monthly_Cost"].notna() & df["Spend_Tier"].isna()]
    if not unbinned_costs.empty:
        raise ValueError(f"Null categories: Found rows with valid cost but missing Spend_Tier:\n{unbinned_costs}")
    print("  - Category Coverage: OK (all valid numerical rows are binned)")
    
    print("All feature validations PASSED successfully.")


# ===========================================================================
# Orchestrator
# ===========================================================================

def main() -> None:
    print("LU-16 :: Feature Engineering & Derived Business Columns")
    print("=" * 60)
    
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input conformed dataset not found at '{INPUT_FILE}'. Please run scripts/merge_sources.py first.")
        
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded conformed dataset: {INPUT_FILE} ({len(df)} rows)")
    
    # Process features using reusable functions
    out = df.copy()
    
    print("\nEngineering features...")
    # 1. Recency days
    out["Deployment_Recency_Days"] = calculate_deployment_recency(out)
    
    # 2. Recency tier (pd.cut)
    out["Recency_Tier"] = segment_recency_tier(out)
    
    # 3. Spend tier (pd.qcut)
    out["Spend_Tier"] = segment_spend_tier(out)
    
    # 4. Incident severity weight (derived)
    out["Incident_Severity_Weight"] = derive_incident_severity_weight(out)
    
    # 5. Composite and Ratio scores
    risk_index, cost_per_risk = compute_cost_risk_score(out)
    out["Cost_Risk_Index"] = risk_index
    out["Cost_per_Risk_Unit"] = cost_per_risk
    
    # Validate features
    validate_features(out)
    
    # Save the output features CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved enriched dataset -> {OUTPUT_FILE}")
    
    # Build structured summary CSV for reporting
    summary_records = []
    for col in ["Deployment_Recency_Days", "Incident_Severity_Weight", "Cost_Risk_Index", "Cost_per_Risk_Unit"]:
        summary_records.append({
            "Feature_Name": col,
            "Min": round(float(out[col].min()), 2) if out[col].notna().any() else np.nan,
            "Max": round(float(out[col].max()), 2) if out[col].notna().any() else np.nan,
            "Mean": round(float(out[col].mean()), 2) if out[col].notna().any() else np.nan,
            "Null_Count": int(out[col].isna().sum())
        })
    
    summary_df = pd.DataFrame(summary_records)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    print(f"Saved report -> {SUMMARY_CSV}")
    print("\nSummary Metrics Table:")
    print(summary_df.to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
