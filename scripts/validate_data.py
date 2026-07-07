"""
LU-14 :: Data Consistency & Validation Rules
============================================

Automated validation framework that decides whether an incoming, already-cleaned
dataset is SAFE for downstream analysis.

The framework runs a battery of independent validation rules against the
deployments table (and cross-checks it against the projects reference table),
isolates every offending row, and emits three artefacts:

    1. data/validation/invalid_records.csv  - every row that failed >= 1 rule,
                                              annotated with the rule(s) it broke.
    2. reports/validation_report.csv        - per-rule pass/fail scoreboard.
    3. docs/lu14_validation_summary.md      - human-readable executive summary.

Design principles:
    * One function per rule -> easy to unit-test and reason about.
    * Each rule returns a boolean Series (True = row is VALID for that rule).
    * A single generic runner aggregates results, so there is NO duplicated
      pass/fail bookkeeping logic scattered across the rules.

Run:
    python scripts/validate_data.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Input datasets (already cleaned by earlier LUs) and the reference table used
# for the foreign-key style check in Rule 5.
DEPLOYMENTS_FILE = os.path.join("data", "cleaned", "deployments.csv")
PROJECTS_FILE = os.path.join("data", "cleaned", "projects.csv")

# Output artefacts.
INVALID_RECORDS_FILE = os.path.join("data", "validation", "invalid_records.csv")
REPORT_FILE = os.path.join("reports", "validation_report.csv")
SUMMARY_FILE = os.path.join("docs", "lu14_validation_summary.md")

# Business constants.
ALLOWED_CLOUD_PROVIDERS = {"AWS", "Azure", "GCP"}
UTILIZATION_MIN, UTILIZATION_MAX = 0, 100
NON_NULLABLE_COLUMNS = ["Project_ID", "Deployment_ID"]


# ===========================================================================
# Data loading
# ===========================================================================
def load_datasets(deployments_path: str, projects_path: str):
    """Load the cleaned deployments table and the projects reference table.

    Dates are parsed up-front so the date-ordering rule can compare them
    natively. `errors="coerce"` turns unparseable dates into NaT rather than
    raising, letting the null/consistency rules flag them downstream.
    """
    deployments = pd.read_csv(deployments_path)
    projects = pd.read_csv(projects_path)

    # Numeric coercion: blanks / bad values become NaN so range rules catch them.
    for col in ["Cost", "CPU_Utilization", "Memory_Utilization"]:
        deployments[col] = pd.to_numeric(deployments[col], errors="coerce")

    # Date coercion for the chronology rule.
    for col in ["Deployment_Date", "Incident_Date"]:
        deployments[col] = pd.to_datetime(deployments[col], errors="coerce")

    return deployments, projects


# ===========================================================================
# Validation rules
# ---------------------------------------------------------------------------
# CONTRACT: every rule takes the deployments DataFrame (plus any extra context)
# and returns a boolean pandas Series aligned to the DataFrame index where
# True  == the row satisfies the rule (VALID)
# False == the row violates the rule (INVALID)
# NaN / NaT values are treated as INVALID because unknown data is not "safe".
# ===========================================================================
def validate_cost(df: pd.DataFrame) -> pd.Series:
    """Rule 1 - Cost must be >= 0.

    Negative cost is economically impossible and usually signals a sign-flip
    or a bad credit/refund merge. NaN (missing cost) is also treated as invalid.
    """
    return df["Cost"].ge(0).fillna(False)


def validate_cpu_range(df: pd.DataFrame) -> pd.Series:
    """Rule 2 - CPU Utilization must be between 0 and 100 (inclusive).

    Utilization is a percentage; values outside [0, 100] indicate a unit or
    parsing error (e.g. a raw core-count leaking into a percent column).
    """
    return df["CPU_Utilization"].between(UTILIZATION_MIN, UTILIZATION_MAX).fillna(False)


def validate_memory_range(df: pd.DataFrame) -> pd.Series:
    """Rule 3 - Memory Utilization must be between 0 and 100 (inclusive).

    Same rationale as CPU: a percentage cannot exceed 100 or drop below 0.
    """
    return df["Memory_Utilization"].between(UTILIZATION_MIN, UTILIZATION_MAX).fillna(False)


def validate_dates(df: pd.DataFrame) -> pd.Series:
    """Rule 4 - Deployment Date cannot be AFTER Incident Date.

    An incident can only occur on or after the resource was deployed. A
    deployment timestamp later than its incident timestamp breaks causality and
    corrupts any time-to-incident / root-cause analysis. Unparseable dates
    (NaT) are treated as invalid.
    """
    valid = df["Deployment_Date"].le(df["Incident_Date"])
    return valid.fillna(False)


def validate_project_reference(df: pd.DataFrame, projects: pd.DataFrame) -> pd.Series:
    """Rule 5 - Referential integrity: every deployment's Project_ID must exist
    in the projects reference table (foreign-key check).

    Orphan Project_IDs mean cost cannot be attributed to a real project, which
    silently drops spend from any per-project roll-up.
    """
    valid_ids = set(projects["Project_ID"].dropna())
    return df["Project_ID"].isin(valid_ids)


def validate_no_nulls(df: pd.DataFrame) -> pd.Series:
    """Rule 6 - No null values allowed in the key columns (Project_ID,
    Deployment_ID).

    These are primary/foreign keys. A null key makes a row impossible to join,
    de-duplicate, or trace, so the entire row is rejected.
    """
    return df[NON_NULLABLE_COLUMNS].notna().all(axis=1)


def validate_cloud_provider(df: pd.DataFrame) -> pd.Series:
    """Rule 7 - Cloud Provider must be one of AWS, Azure, GCP.

    Any other value indicates an unsupported/mistyped provider that downstream
    pricing and cost-allocation logic is not built to handle.
    """
    return df["Cloud_Provider"].isin(ALLOWED_CLOUD_PROVIDERS)


# Rule registry: (human-readable name, callable). Adding a rule = one line here.
# `df` is always passed; rules needing extra context receive it via a lambda so
# the generic runner stays agnostic to individual rule signatures.
def build_rule_registry(projects: pd.DataFrame):
    """Return the ordered list of (rule_name, rule_fn) to execute."""
    return [
        ("Rule 1 - Cost >= 0", validate_cost),
        ("Rule 2 - CPU Utilization in [0,100]", validate_cpu_range),
        ("Rule 3 - Memory Utilization in [0,100]", validate_memory_range),
        ("Rule 4 - Deployment Date <= Incident Date", validate_dates),
        ("Rule 5 - Project_ID exists in projects", lambda df: validate_project_reference(df, projects)),
        ("Rule 6 - No nulls in key columns", validate_no_nulls),
        ("Rule 7 - Cloud Provider in {AWS,Azure,GCP}", validate_cloud_provider),
    ]


# ===========================================================================
# Rule execution engine
# ===========================================================================
def run_validations(df: pd.DataFrame, rules) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute every rule and aggregate the outcome.

    Returns:
        report_df  - one row per rule with Passed/Failed counts and pass %.
        results_df - the input df augmented with:
                        * one boolean column per rule (True = valid)
                        * `Failed_Rules` - comma-joined names of broken rules
                        * `Is_Valid`     - row passed ALL rules
    """
    results_df = df.copy()
    report_rows = []
    failed_rule_labels = pd.Series([""] * len(df), index=df.index)

    for rule_name, rule_fn in rules:
        # `mask` is True where the row is VALID for this rule.
        mask = rule_fn(df)
        results_df[rule_name] = mask

        passed = int(mask.sum())
        failed = int((~mask).sum())
        pass_pct = round(100 * passed / len(df), 2) if len(df) else 0.0
        report_rows.append(
            {
                "Rule_Name": rule_name,
                "Passed_Count": passed,
                "Failed_Count": failed,
                "Pass_Percentage": pass_pct,
            }
        )

        # Accumulate the names of rules each failing row broke (for triage).
        failed_here = ~mask
        failed_rule_labels = failed_rule_labels.where(
            ~failed_here,
            (failed_rule_labels + "; " + rule_name).str.strip("; "),
        )

    results_df["Failed_Rules"] = failed_rule_labels.str.strip("; ")
    results_df["Is_Valid"] = results_df["Failed_Rules"] == ""

    report_df = pd.DataFrame(report_rows)
    return report_df, results_df


# ===========================================================================
# Artefact writers
# ===========================================================================
def write_invalid_records(results_df: pd.DataFrame, path: str) -> pd.DataFrame:
    """Persist only the rows that failed at least one rule, with the reason(s)."""
    original_cols = [c for c in results_df.columns
                     if c not in ("Is_Valid",) and not c.startswith("Rule ")]
    invalid = results_df.loc[~results_df["Is_Valid"], original_cols].copy()
    _ensure_dir(path)
    invalid.to_csv(path, index=False)
    return invalid


def write_report(report_df: pd.DataFrame, path: str) -> None:
    """Persist the per-rule scoreboard."""
    _ensure_dir(path)
    report_df.to_csv(path, index=False)


def write_summary(report_df: pd.DataFrame, results_df: pd.DataFrame, path: str) -> None:
    """Generate the markdown executive summary."""
    total = len(results_df)
    valid = int(results_df["Is_Valid"].sum())
    invalid = total - valid

    # Top failures = rules ordered by highest Failed_Count.
    top_failures = report_df.sort_values("Failed_Count", ascending=False)
    top_failures = top_failures[top_failures["Failed_Count"] > 0]

    lines = []
    lines.append("# LU-14 :: Data Consistency & Validation Summary\n")
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}_\n")

    lines.append("## Overview\n")
    lines.append(f"- **Total Records:** {total}")
    lines.append(f"- **Valid Records:** {valid} ({_pct(valid, total)}%)")
    lines.append(f"- **Invalid Records:** {invalid} ({_pct(invalid, total)}%)\n")

    lines.append("## Validation Results\n")
    lines.append("| Rule | Passed | Failed | Pass % |")
    lines.append("| --- | ---: | ---: | ---: |")
    for _, r in report_df.iterrows():
        lines.append(
            f"| {r['Rule_Name']} | {r['Passed_Count']} | "
            f"{r['Failed_Count']} | {r['Pass_Percentage']}% |"
        )
    lines.append("")

    lines.append("## Top Validation Failures\n")
    if top_failures.empty:
        lines.append("No failures detected. Dataset is safe for analysis. \n")
    else:
        for _, r in top_failures.iterrows():
            lines.append(f"- **{r['Rule_Name']}** — {r['Failed_Count']} failing row(s)")
        lines.append("")

    lines.append("## Recommendations\n")
    lines.extend(_build_recommendations(top_failures))

    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _build_recommendations(top_failures: pd.DataFrame) -> list[str]:
    """Map failing rules to concrete remediation guidance."""
    if top_failures.empty:
        return ["- Promote the dataset to the analysis layer.\n"]

    # Keyword -> advice lookup keeps this readable and non-duplicative.
    advice = {
        "Cost": "Investigate negative/missing costs; check refund & sign handling in the ingestion job.",
        "CPU": "Clamp or re-source CPU metrics; confirm the collector emits a 0-100 percentage.",
        "Memory": "Clamp or re-source Memory metrics; confirm the collector emits a 0-100 percentage.",
        "Incident Date": "Fix event ordering; deployment must precede or equal the incident timestamp.",
        "Project_ID exists": "Backfill missing projects into the reference table or drop orphan deployments.",
        "No nulls": "Enforce NOT NULL on key columns at the source before ingestion.",
        "Cloud Provider": "Standardise provider names to {AWS, Azure, GCP} or add explicit support.",
    }
    recs = []
    for _, r in top_failures.iterrows():
        matched = next((tip for key, tip in advice.items() if key in r["Rule_Name"]), None)
        if matched:
            recs.append(f"- {matched}")
    recs.append("- Re-run validation after remediation; block promotion until pass rate meets SLA.")
    return recs


# ===========================================================================
# Small helpers (single source of truth for repeated operations)
# ===========================================================================
def _ensure_dir(path: str) -> None:
    """Create the parent directory for `path` if it does not yet exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _pct(part: int, whole: int) -> float:
    """Safe percentage helper used by the summary writer."""
    return round(100 * part / whole, 2) if whole else 0.0


# ===========================================================================
# Orchestration
# ===========================================================================
def main() -> None:
    print("LU-14 :: Data Consistency & Validation Rules")
    print("-" * 60)

    deployments, projects = load_datasets(DEPLOYMENTS_FILE, PROJECTS_FILE)
    print(f"Loaded {len(deployments)} deployment rows, {len(projects)} project rows.")

    rules = build_rule_registry(projects)
    report_df, results_df = run_validations(deployments, rules)

    invalid = write_invalid_records(results_df, INVALID_RECORDS_FILE)
    write_report(report_df, REPORT_FILE)
    write_summary(report_df, results_df, SUMMARY_FILE)

    total = len(results_df)
    valid = int(results_df["Is_Valid"].sum())
    print(f"Valid rows  : {valid}/{total}")
    print(f"Invalid rows: {len(invalid)}/{total}")
    print(f"Report      -> {REPORT_FILE}")
    print(f"Invalid CSV -> {INVALID_RECORDS_FILE}")
    print(f"Summary     -> {SUMMARY_FILE}")
    print("-" * 60)
    print(report_df.to_string(index=False))


if __name__ == "__main__":
    main()
