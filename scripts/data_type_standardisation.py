"""
LU-09 :: Data Type Enforcement & Standardisation
================================================

Audits the cleaned cloud cost dataset for data type mismatches and converts
each column into its correct type before analysis:

    * Date        -> pd.to_datetime() with an explicit `format`
    * Currency    -> strip symbols ($ / , / \u20b9 / \u20ac) and cast to float
    * Percentage  -> strip '%' and cast to float
    * Boolean     -> map 0/1 to bool
    * Integer     -> cast to nullable integer

All conversions use errors="coerce": values that cannot be parsed become NaN
and are logged to reports/conversion_errors.csv instead of crashing the run.
The raw/cleaned input is read-only; the standardised result is saved separately.

Run:
    python scripts/data_type_standardisation.py
"""

from __future__ import annotations

import os
import re

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration: input (read-only) and output targets.
# ---------------------------------------------------------------------------
INPUT_FILE = os.path.join("data", "processed", "cloud_cost_dataset_cleaned.csv")
STANDARDIZED_FILE = os.path.join(
    "data", "processed", "cloud_cost_dataset_standardized.csv"
)
REPORTS_DIR = "reports"
DTYPE_BEFORE_CSV = os.path.join(REPORTS_DIR, "dtype_before.csv")
DTYPE_AFTER_CSV = os.path.join(REPORTS_DIR, "dtype_after.csv")
DTYPE_SUMMARY_CSV = os.path.join(REPORTS_DIR, "dtype_conversion_summary.csv")
CONVERSION_ERRORS_CSV = os.path.join(REPORTS_DIR, "conversion_errors.csv")

# ---------------------------------------------------------------------------
# Column type plan. Each column maps to the target category and, for dates,
# the exact strptime format so parsing is deterministic (no silent guessing).
# ---------------------------------------------------------------------------
DATE_COLUMNS = {
    "Deployment_Date": "%Y-%m-%d",
    "Billing_Date": "%d/%m/%Y",
}
CURRENCY_COLUMNS = ["Monthly_Cost"]
PERCENTAGE_COLUMNS = ["CPU_Utilization"]
BOOLEAN_COLUMNS = ["Auto_Scaling_Enabled"]
INTEGER_COLUMNS = ["Resource_Count"]


# ---------------------------------------------------------------------------
# load_dataset(): read the cleaned CSV as all-string to preserve raw tokens
# (e.g. "$1,240.50", "85%") before conversion.
# ---------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load the cleaned dataset. Read as string so symbols survive intact."""
    return pd.read_csv(path, encoding="utf-8", dtype=str)


# ---------------------------------------------------------------------------
# dtype_report(): build a Column Name / Data Type report DataFrame.
# ---------------------------------------------------------------------------
def dtype_report(df: pd.DataFrame, type_col_name: str) -> pd.DataFrame:
    """Return a per-column dtype report with the given type column label."""
    return pd.DataFrame({
        "Column Name": df.columns,
        type_col_name: [str(t) for t in df.dtypes],
    })


# ---------------------------------------------------------------------------
# clean_currency(): strip currency symbols and thousands separators -> float.
# ---------------------------------------------------------------------------
def clean_currency(series: pd.Series) -> pd.Series:
    """Remove $, \u20b9, \u20ac, \u00a3 and commas, then coerce to float."""
    # Keep only digits, decimal point and sign; everything else is noise.
    stripped = series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    # Empty strings (from tokens like "N/A") become NaN via coerce.
    stripped = stripped.replace("", None)
    return pd.to_numeric(stripped, errors="coerce")


# ---------------------------------------------------------------------------
# clean_percentage(): strip '%' -> float.
# ---------------------------------------------------------------------------
def clean_percentage(series: pd.Series) -> pd.Series:
    """Remove the percent sign and coerce to float."""
    stripped = series.astype(str).str.replace("%", "", regex=False).str.strip()
    stripped = stripped.replace("", None)
    return pd.to_numeric(stripped, errors="coerce")


# ---------------------------------------------------------------------------
# standardise(): apply all conversions to a COPY; track failures per column.
# Returns (standardized_df, error_records).
# ---------------------------------------------------------------------------
def standardise(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Convert every configured column to its target type using coerce."""
    out = df.copy()
    errors: list[dict] = []

    def _log_failures(col: str, original: pd.Series, converted: pd.Series):
        """Record rows that were non-null before but NaN/NaT after (parse fail)."""
        original_nonnull = original.notna() & (original.astype(str).str.strip() != "")
        failed = original_nonnull & converted.isna()
        for idx in df.index[failed]:
            errors.append({
                "row_index": int(idx),
                "column": col,
                "original_value": original.loc[idx],
                "reason": "Could not parse to target type (coerced to NaN)",
            })

    # --- DATE COLUMNS: explicit format, coerce invalid dates to NaT ---
    for col, fmt in DATE_COLUMNS.items():
        if col in out.columns:
            converted = pd.to_datetime(out[col], format=fmt, errors="coerce")
            _log_failures(col, out[col], converted)
            out[col] = converted

    # --- CURRENCY COLUMNS: strip symbols/commas -> float ---
    for col in CURRENCY_COLUMNS:
        if col in out.columns:
            converted = clean_currency(out[col])
            _log_failures(col, out[col], converted)
            out[col] = converted

    # --- PERCENTAGE COLUMNS: strip '%' -> float ---
    for col in PERCENTAGE_COLUMNS:
        if col in out.columns:
            converted = clean_percentage(out[col])
            _log_failures(col, out[col], converted)
            out[col] = converted

    # --- INTEGER COLUMNS: numeric coerce -> nullable Int64 ---
    for col in INTEGER_COLUMNS:
        if col in out.columns:
            converted = pd.to_numeric(out[col], errors="coerce")
            _log_failures(col, out[col], converted)
            # Nullable integer keeps NaN-safe integers (no float coercion).
            out[col] = converted.astype("Int64")

    # --- BOOLEAN COLUMNS: map 0/1 (and true/false text) -> bool ---
    for col in BOOLEAN_COLUMNS:
        if col in out.columns:
            numeric = pd.to_numeric(out[col], errors="coerce")
            _log_failures(col, out[col], numeric)
            # 1 -> True, 0 -> False, unparseable -> False (after logging).
            out[col] = numeric.fillna(0).astype(int).astype(bool)

    return out, errors


# ---------------------------------------------------------------------------
# save_reports(): write before/after/summary/error CSVs.
# ---------------------------------------------------------------------------
def save_reports(
    before: pd.DataFrame,
    after: pd.DataFrame,
    errors: list[dict],
) -> pd.DataFrame:
    """Persist all dtype reports and return the comparison summary."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # BEFORE report.
    before.to_csv(DTYPE_BEFORE_CSV, index=False)
    # AFTER report.
    after.to_csv(DTYPE_AFTER_CSV, index=False)

    # Comparison summary: Column / Before / After.
    summary = pd.DataFrame({
        "Column": before["Column Name"],
        "Before": before["Current Data Type"].values,
        "After": after["Updated Data Type"].values,
    })
    summary.to_csv(DTYPE_SUMMARY_CSV, index=False)

    # Conversion errors (may be empty -> header-only file).
    error_df = pd.DataFrame(
        errors,
        columns=["row_index", "column", "original_value", "reason"],
    )
    error_df.to_csv(CONVERSION_ERRORS_CSV, index=False)

    return summary


def main() -> None:
    # STEP 3: Load cleaned dataset (read-only, all strings).
    df = load_dataset(INPUT_FILE)

    # STEP 4: BEFORE report.
    before = dtype_report(df, "Current Data Type")
    print("=" * 60)
    print("DTYPE BEFORE")
    print("=" * 60)
    print(before.to_string(index=False))
    print()

    # STEP 5 + 6: Apply conversions with safe coercion + failure logging.
    standardized, errors = standardise(df)

    # STEP 7: AFTER report.
    after = dtype_report(standardized, "Updated Data Type")
    print("=" * 60)
    print("DTYPE AFTER")
    print("=" * 60)
    print(after.to_string(index=False))
    print()

    # STEP 8 + 6: Save all reports (before/after/summary/errors).
    summary = save_reports(before, after, errors)
    print("=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(summary.to_string(index=False))
    print()
    print(f"Conversion failures logged: {len(errors)}")

    # STEP 9: Save standardized dataset separately.
    os.makedirs(os.path.dirname(STANDARDIZED_FILE), exist_ok=True)
    standardized.to_csv(STANDARDIZED_FILE, index=False)

    print("\nGenerated:")
    for path in (
        DTYPE_BEFORE_CSV, DTYPE_AFTER_CSV, DTYPE_SUMMARY_CSV,
        CONVERSION_ERRORS_CSV, STANDARDIZED_FILE,
    ):
        print(f"  {path}")


if __name__ == "__main__":
    main()
