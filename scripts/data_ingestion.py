"""
LU-05 :: CSV & JSON Data Ingestion
==================================

Imports both CSV and JSON business datasets into Pandas DataFrames and prepares
them for downstream analysis.

Workflow:
    1. load_csv_data()          - read CSV with explicit encoding & delimiter
    2. load_json_data()         - read nested JSON and flatten with json_normalize
    3. display_dataset_summary()- print shape, columns, dtypes, first 5 rows
    4. export processed outputs to outputs/

Run:
    python scripts/data_ingestion.py
"""

from __future__ import annotations

import json
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration: input datasets and processed output targets.
# ---------------------------------------------------------------------------
CSV_INPUT = os.path.join("data", "raw", "cloud_costs.csv")
JSON_INPUT = os.path.join("data", "raw", "cloud_deployments.json")

OUTPUT_DIR = "outputs"
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "cloud_costs_processed.csv")
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "cloud_deployments_processed.csv")


# ---------------------------------------------------------------------------
# Helper: load CSV data
# ---------------------------------------------------------------------------
def load_csv_data(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Encoding and delimiter are specified EXPLICITLY (never relying on pandas
    defaults) so ingestion is deterministic across environments.
    """
    df = pd.read_csv(
        path,
        encoding="utf-8",  # explicit: do not rely on default
        delimiter=",",     # explicit: do not rely on default
    )
    return df


# ---------------------------------------------------------------------------
# Helper: load JSON data
# ---------------------------------------------------------------------------
def load_json_data(path: str) -> pd.DataFrame:
    """Load a nested JSON file and flatten it into a tabular DataFrame.

    Uses pd.json_normalize() with a '.' separator so nested keys become dotted
    column names (e.g. service.name, metrics.cpu_usage), matching the expected
    downstream schema.
    """
    with open(path, "r", encoding="utf-8") as fh:
        records = json.load(fh)

    # Flatten nested dicts: service.* and metrics.* become dotted columns.
    df = pd.json_normalize(records, sep=".")
    return df


# ---------------------------------------------------------------------------
# Helper: display dataset summary
# ---------------------------------------------------------------------------
def display_dataset_summary(df: pd.DataFrame, title: str) -> None:
    """Print a standardized summary: shape, columns, dtypes, first 5 rows."""
    print("=" * 49)
    print(title)
    print("=" * len(title))
    print(f"\nShape: {df.shape}")

    print("\nColumns:")
    for col in df.columns:
        print(col)

    print("\nDtypes:")
    print(df.dtypes.to_string())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print()


def main() -> None:
    # Ensure the output directory exists before exporting.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- CSV ingestion ---
    csv_df = load_csv_data(CSV_INPUT)
    display_dataset_summary(csv_df, "CSV INGESTION SUMMARY")

    # --- JSON ingestion (flattened) ---
    json_df = load_json_data(JSON_INPUT)
    display_dataset_summary(json_df, "JSON INGESTION SUMMARY")

    # --- Export processed datasets ---
    csv_df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8")
    json_df.to_csv(JSON_OUTPUT, index=False, encoding="utf-8")

    print("=" * 49)
    print("Processed outputs written:")
    print(f"  {CSV_OUTPUT}")
    print(f"  {JSON_OUTPUT}")


if __name__ == "__main__":
    main()
