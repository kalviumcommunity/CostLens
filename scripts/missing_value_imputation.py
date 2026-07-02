"""
LU-08 :: Missing Value Detection & Imputation
=============================================

Detects missing values across the cloud cost dataset, applies business-aware
imputation strategies, documents every decision, compares before/after null
counts and writes a cleaned dataset to a SEPARATE file.

The raw dataset is never modified: all imputation happens on an in-memory copy
and the result is written to data/processed/.

Imputation strategies applied:
    * Numerical  -> Median imputation  (Monthly_Cost, CPU_Usage)
    * Categorical-> Mode imputation    (Team_Name, Environment)
    * Time-series-> Forward fill       (Deployment_Date)
    * Business   -> Constant "Unknown" (Cost_Center)

Run:
    python scripts/missing_value_imputation.py
"""

from __future__ import annotations

import csv
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration: input (raw, read-only) and output targets.
# ---------------------------------------------------------------------------
RAW_FILE = os.path.join("data", "raw", "cloud_cost_dataset.csv")
CLEANED_FILE = os.path.join("data", "processed", "cloud_cost_dataset_cleaned.csv")
REPORTS_DIR = "reports"
DECISIONS_MD = os.path.join(REPORTS_DIR, "imputation_decisions.md")
NULL_COMPARISON_CSV = os.path.join(REPORTS_DIR, "null_comparison.csv")

# ---------------------------------------------------------------------------
# Imputation plan: column -> (method, reason).
# Each entry drives BOTH the imputation logic and the decision documentation,
# so the code and the report can never drift apart.
# ---------------------------------------------------------------------------
IMPUTATION_PLAN: dict[str, dict[str, str]] = {
    "Monthly_Cost": {
        "method": "median",
        "reason": "Numeric spend column; median is less sensitive to outliers "
                  "than the mean, so extreme bills do not skew the fill value.",
    },
    "CPU_Usage": {
        "method": "median",
        "reason": "Numeric utilisation metric; median preserves the central "
                  "tendency without being distorted by spiky workloads.",
    },
    "Team_Name": {
        "method": "mode",
        "reason": "Categorical owner; the most frequent team is the safest "
                  "default and keeps the category distribution realistic.",
    },
    "Environment": {
        "method": "mode",
        "reason": "Categorical lifecycle stage with few values; mode assigns "
                  "the most common environment as a sensible default.",
    },
    "Deployment_Date": {
        "method": "ffill",
        "reason": "Time-series column ordered by deployment; forward fill "
                  "carries the last known date forward to keep chronology.",
    },
    "Cost_Center": {
        "method": "constant:Unknown",
        "reason": "Business rule: a missing cost center cannot be guessed, so "
                  "it is explicitly flagged as 'Unknown' for finance review.",
    },
}


# ---------------------------------------------------------------------------
# load_dataset(): read the raw CSV (read-only source).
# ---------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load the raw dataset. This DataFrame is treated as immutable source."""
    return pd.read_csv(path, encoding="utf-8", delimiter=",")


# ---------------------------------------------------------------------------
# build_missing_report(): per-column name, dtype, null count, null percentage.
# ---------------------------------------------------------------------------
def build_missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a tidy missing-value report DataFrame."""
    row_count = len(df)
    records = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        records.append({
            "Column Name": col,
            "Data Type": str(df[col].dtype),
            "Null Count": null_count,
            "Null Percentage": round((null_count / row_count) * 100, 2)
            if row_count else 0.0,
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# print_missing_report(): display the report in the console.
# ---------------------------------------------------------------------------
def print_missing_report(report: pd.DataFrame) -> None:
    """Print the missing value report to the terminal."""
    print("=" * 60)
    print("MISSING VALUE REPORT")
    print("=" * 60)
    print(report.to_string(index=False))
    print()


# ---------------------------------------------------------------------------
# apply_imputation(): apply the configured strategy to a COPY of the raw data.
# ---------------------------------------------------------------------------
def apply_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the imputation plan to a copy; the raw frame stays untouched."""
    # .copy() guarantees the raw DataFrame (and file) is never mutated.
    cleaned = df.copy()

    for col, plan in IMPUTATION_PLAN.items():
        # Skip columns not present in this dataset version.
        if col not in cleaned.columns:
            continue

        method = plan["method"]

        if method == "median":
            # Numerical: fill with the column median.
            fill_value = cleaned[col].median()
            cleaned[col] = cleaned[col].fillna(fill_value)

        elif method == "mode":
            # Categorical: fill with the most frequent value.
            mode_series = cleaned[col].mode(dropna=True)
            if not mode_series.empty:
                cleaned[col] = cleaned[col].fillna(mode_series.iloc[0])

        elif method == "ffill":
            # Time-series: carry the last known value forward, then back-fill
            # any leading gaps so no null remains at the top of the column.
            cleaned[col] = cleaned[col].ffill().bfill()

        elif method.startswith("constant:"):
            # Business rule: replace with an explicit constant (e.g. "Unknown").
            constant = method.split("constant:", 1)[1]
            cleaned[col] = cleaned[col].fillna(constant)

    return cleaned


# ---------------------------------------------------------------------------
# write_decisions(): document every imputation decision as Markdown.
# ---------------------------------------------------------------------------
def write_decisions(before_report: pd.DataFrame) -> None:
    """Write reports/imputation_decisions.md documenting each decision."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Map column -> missing percentage for the decision log.
    pct_by_col = dict(
        zip(before_report["Column Name"], before_report["Null Percentage"])
    )

    # Human-readable label for each method key.
    method_label = {
        "median": "Median",
        "mode": "Mode",
        "ffill": "Forward Fill",
    }

    lines = ["# Imputation Decisions — LU-08\n"]
    lines.append(
        "Every column with missing values and the business-aware strategy "
        "used to resolve it. The raw dataset is preserved; imputation is "
        "applied only to the cleaned copy.\n"
    )
    lines.append("| Column | Missing % | Method Used | Reason |")
    lines.append("| ------ | --------- | ----------- | ------ |")

    for col, plan in IMPUTATION_PLAN.items():
        if col not in pct_by_col:
            continue
        method = plan["method"]
        if method.startswith("constant:"):
            label = f"Constant \"{method.split('constant:', 1)[1]}\""
        else:
            label = method_label.get(method, method)
        pct = pct_by_col[col]
        lines.append(f"| {col} | {pct}% | {label} | {plan['reason']} |")

    with open(DECISIONS_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# write_null_comparison(): before vs after null counts per column.
# ---------------------------------------------------------------------------
def write_null_comparison(
    raw: pd.DataFrame, cleaned: pd.DataFrame
) -> pd.DataFrame:
    """Write reports/null_comparison.csv and return the comparison frame."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    records = []
    for col in raw.columns:
        records.append({
            "Column": col,
            "Nulls Before": int(raw[col].isna().sum()),
            "Nulls After": int(cleaned[col].isna().sum()),
        })
    comparison = pd.DataFrame(records)

    with open(NULL_COMPARISON_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["Column", "Nulls Before", "Nulls After"]
        )
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    return comparison


# ---------------------------------------------------------------------------
# save_cleaned(): persist the cleaned dataset to data/processed/.
# ---------------------------------------------------------------------------
def save_cleaned(cleaned: pd.DataFrame) -> None:
    """Write the cleaned dataset to a separate file (raw stays intact)."""
    os.makedirs(os.path.dirname(CLEANED_FILE), exist_ok=True)
    cleaned.to_csv(CLEANED_FILE, index=False)


def main() -> None:
    # STEP 1: Load raw dataset (read-only).
    raw = load_dataset(RAW_FILE)

    # STEP 2: Build and display the missing value report.
    before_report = build_missing_report(raw)
    print_missing_report(before_report)

    # STEP 3: Apply imputation strategies to a copy.
    cleaned = apply_imputation(raw)

    # STEP 4: Document every imputation decision.
    write_decisions(before_report)

    # STEP 5: Generate before/after null comparison.
    comparison = write_null_comparison(raw, cleaned)
    print("=" * 60)
    print("NULL COMPARISON (Before vs After)")
    print("=" * 60)
    print(comparison.to_string(index=False))
    print()

    # STEP 6: Save cleaned dataset separately.
    save_cleaned(cleaned)

    print("Generated:")
    print(f"  {DECISIONS_MD}")
    print(f"  {NULL_COMPARISON_CSV}")
    print(f"  {CLEANED_FILE}")
    print(f"\nRaw dataset untouched: {RAW_FILE}")


if __name__ == "__main__":
    main()
