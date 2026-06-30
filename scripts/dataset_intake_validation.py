"""
LU-04 :: Dataset Intake & Source Validation
===========================================

Validates an incoming dataset BEFORE any cleaning or analysis occurs.

Workflow stages:
    A. File validation     - exists, non-empty, parses as CSV
    B. Schema validation    - compare actual vs expected columns
    C. Encoding validation  - detect encoding with a fallback strategy
    D. Dataset metadata     - capture descriptive facts about the file
    E. Structured report    - write outputs/intake_validation_report.json
    F. Logging              - print a human-readable summary to the terminal

Run:
    python scripts/dataset_intake_validation.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Path of the dataset under inspection and where the report is written.
INPUT_FILE = os.path.join("data", "raw", "cloud_cost_sample.csv")
REPORT_FILE = os.path.join("outputs", "intake_validation_report.json")

# The schema every incoming cloud-cost dataset MUST conform to.
EXPECTED_COLUMNS = [
    "timestamp",
    "service_name",
    "environment",
    "cost_usd",
    "deployment_id",
]

# Encodings attempted, in priority order, by the fallback strategy.
ENCODING_CANDIDATES = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]


# ===========================================================================
# A. FILE VALIDATION
# ===========================================================================
def validate_file(path: str) -> dict:
    """Confirm the file exists, is non-empty and is parseable as CSV.

    Returns a dict of independent boolean checks plus any error message so the
    caller can decide overall pass/fail without raising mid-pipeline.
    """
    result = {
        "file_exists": False,
        "file_non_empty": False,
        "valid_csv": False,
        "error": None,
    }

    # Check 1: existence on disk.
    if not os.path.isfile(path):
        result["error"] = f"File not found: {path}"
        return result
    result["file_exists"] = True

    # Check 2: file is not zero bytes.
    if os.path.getsize(path) == 0:
        result["error"] = "File is empty (0 bytes)"
        return result
    result["file_non_empty"] = True

    # Check 3: pandas can actually parse it as CSV.
    try:
        pd.read_csv(path, nrows=5)
        result["valid_csv"] = True
    except Exception as exc:  # noqa: BLE001 - report any parse failure verbatim
        result["error"] = f"CSV parse error: {exc}"

    return result


# ===========================================================================
# C. ENCODING VALIDATION (defined before metadata because metadata needs it)
# ===========================================================================
def detect_encoding(path: str) -> str:
    """Detect file encoding.

    Primary strategy: use `chardet` when installed (statistical detection).
    Fallback strategy: if chardet is unavailable or unconfident, try a list of
    common encodings in turn and return the first one that decodes cleanly.
    Final fallback: 'utf-8'.
    """
    # --- Primary: chardet, if available ---
    try:
        import chardet  # imported lazily so the script runs without it

        with open(path, "rb") as fh:
            raw = fh.read()
        guess = chardet.detect(raw)
        if guess and guess.get("encoding") and guess.get("confidence", 0) >= 0.5:
            return guess["encoding"].lower()
    except ImportError:
        pass  # chardet not installed -> drop to manual fallback
    except Exception:
        pass  # any detection error -> drop to manual fallback

    # --- Fallback: try candidate encodings until one decodes the whole file ---
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ENCODING_CANDIDATES:
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue

    # --- Final fallback ---
    return "utf-8"


# ===========================================================================
# B. SCHEMA VALIDATION
# ===========================================================================
def validate_schema(path: str, encoding: str) -> dict:
    """Compare actual columns against the expected schema.

    Detects both missing columns (expected but absent) and extra columns
    (present but not expected) and stores them for the report.
    """
    df = pd.read_csv(path, encoding=encoding)
    actual_columns = list(df.columns)

    missing = [c for c in EXPECTED_COLUMNS if c not in actual_columns]
    extra = [c for c in actual_columns if c not in EXPECTED_COLUMNS]

    return {
        "actual_columns": actual_columns,
        "missing_columns": missing,
        "extra_columns": extra,
        "schema_ok": len(missing) == 0 and len(extra) == 0,
        "row_count": int(len(df)),
        "column_count": int(len(actual_columns)),
    }


# ===========================================================================
# D. DATASET METADATA
# ===========================================================================
def build_metadata(path: str, encoding: str, schema: dict) -> dict:
    """Capture descriptive facts about the dataset for traceability."""
    return {
        "file_name": os.path.basename(path),
        "file_path": path,
        "file_size_bytes": os.path.getsize(path),
        "row_count": schema["row_count"],
        "column_count": schema["column_count"],
        "encoding": encoding,
        "validation_timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ===========================================================================
# E. STRUCTURED REPORT
# ===========================================================================
def generate_report(path: str) -> dict:
    """Run every validation stage and assemble the final report dict."""
    file_checks = validate_file(path)

    # If the file itself failed, short-circuit with a FAIL report.
    if not file_checks["valid_csv"]:
        return {
            "file_name": os.path.basename(path),
            "file_checks": file_checks,
            "validation_status": "FAIL",
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    encoding = detect_encoding(path)
    schema = validate_schema(path, encoding)
    metadata = build_metadata(path, encoding, schema)

    # Overall status passes only when file AND schema checks pass.
    status = "PASS" if (file_checks["valid_csv"] and schema["schema_ok"]) else "FAIL"

    report = {
        "file_name": metadata["file_name"],
        "file_path": metadata["file_path"],
        "file_size_bytes": metadata["file_size_bytes"],
        "row_count": metadata["row_count"],
        "column_count": metadata["column_count"],
        "encoding": metadata["encoding"],
        "expected_columns": EXPECTED_COLUMNS,
        "actual_columns": schema["actual_columns"],
        "missing_columns": schema["missing_columns"],
        "extra_columns": schema["extra_columns"],
        "file_checks": file_checks,
        "validation_status": status,
        "validation_timestamp": metadata["validation_timestamp"],
    }
    return report


def write_report(report: dict, path: str) -> None:
    """Persist the report as pretty-printed JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)


# ===========================================================================
# F. LOGGING
# ===========================================================================
def print_summary(report: dict) -> None:
    """Print a concise, human-readable validation summary to the terminal."""
    print("Dataset Intake Report")
    print("---------------------")
    print(f"File:    {report.get('file_name')}")
    print(f"Rows:    {report.get('row_count', 'N/A')}")
    print(f"Columns: {report.get('column_count', 'N/A')}")
    print(f"Encoding: {report.get('encoding', 'N/A')}")

    missing = report.get("missing_columns", [])
    extra = report.get("extra_columns", [])
    schema_state = "PASS" if not missing and not extra else "FAIL"
    print(f"Schema Validation: {schema_state}")
    if missing:
        print(f"  Missing columns: {missing}")
    if extra:
        print(f"  Extra columns:   {extra}")

    print(f"Overall Status: {report.get('validation_status')}")


# ===========================================================================
# ENTRY POINT
# ===========================================================================
def main() -> None:
    report = generate_report(INPUT_FILE)
    write_report(report, REPORT_FILE)
    print_summary(report)
    print(f"\nReport written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
