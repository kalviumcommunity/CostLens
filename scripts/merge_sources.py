"""
LU-15 :: Multi-Source Merging & Join Validation
===============================================

Combine three cloud datasets (billing, deployment history, incident logs) into a
single TRUSTED analytical dataset, while proving the joins do not silently:
    * drop rows (row loss),
    * fan-out into duplicates (cardinality blow-up), or
    * introduce inconsistent / conflicting key data.

Pipeline stages:
    A. Load          - read all three sources.
    B. Summarise     - shape / columns / dtypes for each source.
    C. Validate keys - null & duplicate Project_ID audit per source.
    D. Join study    - inner / left / outer on billing + deployment_history,
                       with before/after row-count accounting.
    E. Unmatched     - isolate keys that live in only one source.
    F. Final dataset - LEFT JOIN billing <- deployment <- incident on Project_ID.
    G. Validate merge- duplicate cols, duplicate keys, null audit, key conflicts.

Artefacts written:
    reports/join_validation_report.csv
    data/validation/unmatched_billing.csv
    data/validation/unmatched_deployments.csv
    data/validation/unmatched_incidents.csv
    data/processed/final_merged_dataset.csv
    docs/lu15_merge_summary.md  (authored separately, populated from these results)

Run:
    python scripts/merge_sources.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BILLING_FILE = os.path.join("data", "raw", "billing_data.csv")
DEPLOYMENT_FILE = os.path.join("data", "raw", "deployment_history.csv")
INCIDENT_FILE = os.path.join("data", "raw", "incident_logs.csv")

JOIN_REPORT_FILE = os.path.join("reports", "join_validation_report.csv")
UNMATCHED_BILLING_FILE = os.path.join("data", "validation", "unmatched_billing.csv")
UNMATCHED_DEPLOY_FILE = os.path.join("data", "validation", "unmatched_deployments.csv")
UNMATCHED_INCIDENT_FILE = os.path.join("data", "validation", "unmatched_incidents.csv")
FINAL_DATASET_FILE = os.path.join("data", "processed", "final_merged_dataset.csv")
MERGE_SUMMARY_FILE = os.path.join("docs", "lu15_merge_summary.md")

JOIN_KEY = "Project_ID"


# ===========================================================================
# A. Load
# ===========================================================================
def load_sources():
    """Load the three raw datasets. Dates parsed for downstream analysis."""
    billing = pd.read_csv(BILLING_FILE)
    deployment = pd.read_csv(DEPLOYMENT_FILE, parse_dates=["Deployment_Date"])
    incident = pd.read_csv(INCIDENT_FILE, parse_dates=["Incident_Date"])
    return billing, deployment, incident


# ===========================================================================
# B. Summarise
# ===========================================================================
def summarise_dataset(name: str, df: pd.DataFrame) -> None:
    """Print shape, columns and dtypes for a single source."""
    print(f"\n[{name}]")
    print(f"  Shape  : {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"  Columns: {list(df.columns)}")
    print("  Dtypes :")
    for col, dtype in df.dtypes.items():
        print(f"    - {col}: {dtype}")


# ===========================================================================
# C. Join-key validation
# ===========================================================================
def validate_join_key(name: str, df: pd.DataFrame, key: str = JOIN_KEY) -> dict:
    """Audit a source's join key for nulls and duplicates.

    Duplicate keys are legal in billing (a project owns many resources) but are
    the root cause of join fan-out, so we report them for transparency rather
    than treating them as errors.
    """
    null_count = int(df[key].isna().sum())
    dup_mask = df[key].duplicated(keep=False) & df[key].notna()
    dup_count = int(dup_mask.sum())
    unique_keys = int(df[key].nunique(dropna=True))

    finding = {
        "Dataset": name,
        "Total_Rows": len(df),
        "Unique_Keys": unique_keys,
        "Null_Keys": null_count,
        "Duplicate_Keys": dup_count,
    }
    print(
        f"  {name}: rows={len(df)} unique_keys={unique_keys} "
        f"nulls={null_count} duplicate_key_rows={dup_count}"
    )
    return finding


# ===========================================================================
# D. Join study with row accounting
# ===========================================================================
def study_join(left: pd.DataFrame, right: pd.DataFrame, how: str,
               key: str = JOIN_KEY) -> dict:
    """Run one join and account for rows added/lost vs the left source.

    Baseline is the left (billing) row count. `Rows_Added` = fan-out or newly
    introduced right-only rows; `Rows_Lost` = left rows with no match that an
    inner join would drop.
    """
    before = len(left)
    merged = left.merge(right, on=key, how=how, suffixes=("_billing", "_deploy"))
    after = len(merged)

    # Left keys that found no match on the right (would be dropped by INNER).
    matched_keys = set(left[key].dropna()) & set(right[key].dropna())
    left_unmatched = left[~left[key].isin(matched_keys) & left[key].notna()]
    rows_lost = len(left_unmatched) if how == "inner" else 0

    return {
        "Join_Type": how.upper(),
        "Left_Source": "billing_data",
        "Right_Source": "deployment_history",
        "Rows_Before": before,
        "Rows_After": after,
        "Rows_Added": max(after - before, 0),
        "Rows_Lost": rows_lost,
    }


def build_join_report(billing: pd.DataFrame, deployment: pd.DataFrame) -> pd.DataFrame:
    """Run inner/left/outer joins and assemble the row-accounting report."""
    rows = [study_join(billing, deployment, how) for how in ("inner", "left", "outer")]
    return pd.DataFrame(rows)


# ===========================================================================
# E. Unmatched-record detection
# ===========================================================================
def find_unmatched(df: pd.DataFrame, other_keys: set, key: str = JOIN_KEY) -> pd.DataFrame:
    """Return rows whose key does not appear in `other_keys` (excludes nulls)."""
    return df[~df[key].isin(other_keys) & df[key].notna()].copy()


def detect_all_unmatched(billing, deployment, incident):
    """Isolate records that exist in only one source relative to the others.

    A key is 'matched' for a source if it appears in ANY of the other two
    sources; anything else is orphaned and cannot be enriched by a join.
    """
    b_keys = set(billing[JOIN_KEY].dropna())
    d_keys = set(deployment[JOIN_KEY].dropna())
    i_keys = set(incident[JOIN_KEY].dropna())

    unmatched_billing = find_unmatched(billing, d_keys | i_keys)
    unmatched_deploy = find_unmatched(deployment, b_keys | i_keys)
    unmatched_incident = find_unmatched(incident, b_keys | d_keys)
    return unmatched_billing, unmatched_deploy, unmatched_incident


# ===========================================================================
# F. Final analytical dataset
# ===========================================================================
def build_final_dataset(billing, deployment, incident) -> pd.DataFrame:
    """Build the trusted analytical dataset via chained LEFT JOINs on Project_ID.

    LEFT is anchored on billing because billing is the source of financial truth:
    every dollar of spend MUST survive the merge. Deployment and incident context
    is enriched on where available and left NULL where not, without ever dropping
    a billing row.
    """
    merged = billing.merge(
        deployment, on=JOIN_KEY, how="left", suffixes=("", "_deploy")
    )
    merged = merged.merge(
        incident, on=JOIN_KEY, how="left", suffixes=("", "_incident")
    )
    return merged


# ===========================================================================
# G. Merged-dataset validation
# ===========================================================================
def validate_merged(merged: pd.DataFrame, billing: pd.DataFrame) -> dict:
    """Sanity-check the final dataset after merging.

    Checks:
      * Duplicate column names (suffix collision / accidental double-merge).
      * Billing-row preservation (LEFT JOIN must not lose financial rows).
      * Null audit per column (expected for enrichment, flagged for awareness).
      * Key conflicts: a billing Project_ID that vanished from the merged output.
    """
    duplicate_cols = merged.columns[merged.columns.duplicated()].tolist()

    billing_keys = set(billing[JOIN_KEY].dropna())
    merged_keys = set(merged[JOIN_KEY].dropna())
    key_conflicts = sorted(billing_keys - merged_keys)  # billing keys that disappeared

    null_audit = {col: int(merged[col].isna().sum())
                  for col in merged.columns if merged[col].isna().any()}

    # Preservation: every billing key survives (no conflicts) AND row count never
    # shrinks. Fan-out from the incident join may legitimately INCREASE rows, so
    # we assert >=, not equality.
    billing_rows_preserved = (not key_conflicts) and (len(merged) >= len(billing))

    return {
        "final_rows": len(merged),
        "billing_rows": len(billing),
        "billing_rows_preserved": billing_rows_preserved,
        "duplicate_columns": duplicate_cols,
        "duplicate_project_ids": int(
            merged[JOIN_KEY].duplicated(keep=False).sum()
        ),
        "key_conflicts": key_conflicts,
        "null_audit": null_audit,
    }


# ===========================================================================
# Helpers
# ===========================================================================
def _ensure_dir(path: str) -> None:
    """Create the parent directory for `path` if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _write_csv(df: pd.DataFrame, path: str) -> None:
    """Write a DataFrame to CSV, creating parent dirs first."""
    _ensure_dir(path)
    df.to_csv(path, index=False)


# ===========================================================================
# Documentation writer
# ===========================================================================
def write_merge_summary(path, key_findings, join_report, unmatched, merge_validation):
    """Generate docs/lu15_merge_summary.md from computed results."""
    ub, ud, ui = unmatched
    lines = []
    lines.append("# LU-15 :: Multi-Source Merging & Join Validation Summary\n")
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}_\n")

    lines.append("## Why Each Join Type Exists\n")
    lines.append("- **INNER JOIN** — keeps only projects present in *both* sources. "
                 "Use when analysis requires complete billing **and** deployment context "
                 "(e.g. cost-per-deployment). Trades coverage for completeness.")
    lines.append("- **LEFT JOIN** — keeps every billing row, enriches with deployment "
                 "data where it exists. Preserves 100% of spend; unmatched context is NULL.")
    lines.append("- **OUTER JOIN** — keeps every row from *both* sources, matched or not. "
                 "Best for auditing/reconciliation to surface orphans on either side.\n")

    lines.append("## Why LEFT JOIN Was Selected for the Final Dataset\n")
    lines.append("Billing is the **source of financial truth** — every dollar of spend must "
                 "survive the merge. A LEFT JOIN anchored on `billing_data` guarantees no "
                 "cost row is dropped, while deployment and incident data enrich rows that "
                 "have matches and stay NULL where they do not. An INNER JOIN would silently "
                 "discard spend for projects lacking a deployment/incident record, "
                 "under-reporting total cost.\n")

    lines.append("## Business Reasoning\n")
    lines.append("- Under-counting spend is unacceptable for FinOps reporting -> never drop billing rows.")
    lines.append("- Missing deployment/incident context is acceptable and explicitly modelled as NULL.")
    lines.append("- Orphan keys are surfaced (not hidden) so data owners can backfill sources.\n")

    lines.append("## Join Key Findings\n")
    lines.append("| Dataset | Rows | Unique Keys | Null Keys | Duplicate-Key Rows |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for f in key_findings:
        lines.append(f"| {f['Dataset']} | {f['Total_Rows']} | {f['Unique_Keys']} | "
                     f"{f['Null_Keys']} | {f['Duplicate_Keys']} |")
    lines.append("")

    lines.append("## Join Validation Results (billing + deployment_history)\n")
    lines.append("| Join Type | Rows Before | Rows After | Rows Added | Rows Lost |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for _, r in join_report.iterrows():
        lines.append(f"| {r['Join_Type']} | {r['Rows_Before']} | {r['Rows_After']} | "
                     f"{r['Rows_Added']} | {r['Rows_Lost']} |")
    lines.append("")

    lines.append("## Unmatched Key Findings\n")
    lines.append(f"- **billing_data only:** {len(ub)} row(s) — "
                 f"projects `{sorted(ub[JOIN_KEY].unique())}`")
    lines.append(f"- **deployment_history only:** {len(ud)} row(s) — "
                 f"projects `{sorted(ud[JOIN_KEY].unique())}`")
    lines.append(f"- **incident_logs only:** {len(ui)} row(s) — "
                 f"projects `{sorted(ui[JOIN_KEY].unique())}`\n")

    lines.append("## Merged Dataset Validation\n")
    lines.append(f"- Final rows: **{merge_validation['final_rows']}**")
    lines.append(f"- Duplicate columns: `{merge_validation['duplicate_columns'] or 'none'}`")
    lines.append(f"- Rows with duplicate Project_ID (expected fan-out): "
                 f"**{merge_validation['duplicate_project_ids']}**")
    lines.append(f"- Key conflicts (billing keys lost in merge): "
                 f"`{merge_validation['key_conflicts'] or 'none'}`")
    lines.append(f"- Null audit (col -> null count): `{merge_validation['null_audit']}`\n")

    lines.append("## Recommendations\n")
    lines.append("- Backfill orphan projects into the missing source(s) or tag them as "
                 "out-of-scope so reconciliation stays clean.")
    lines.append("- Enforce NOT NULL on `Project_ID` at ingestion for all three sources.")
    lines.append("- Treat duplicate-key fan-out explicitly: pre-aggregate billing to project "
                 "grain before merging if a 1-row-per-project analytical grain is required.")
    lines.append("- Re-run this validation on every data refresh; block promotion if billing "
                 "rows are lost or unexpected duplicate columns appear.\n")

    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ===========================================================================
# Orchestration
# ===========================================================================
def main() -> None:
    print("LU-15 :: Multi-Source Merging & Join Validation")
    print("=" * 60)

    # A + B. Load and summarise.
    billing, deployment, incident = load_sources()
    summarise_dataset("billing_data", billing)
    summarise_dataset("deployment_history", deployment)
    summarise_dataset("incident_logs", incident)

    # C. Join-key validation.
    print("\nJoin-key validation:")
    key_findings = [
        validate_join_key("billing_data", billing),
        validate_join_key("deployment_history", deployment),
        validate_join_key("incident_logs", incident),
    ]

    # D. Join study + report.
    join_report = build_join_report(billing, deployment)
    _write_csv(join_report, JOIN_REPORT_FILE)
    print(f"\nJoin report -> {JOIN_REPORT_FILE}")
    print(join_report.to_string(index=False))

    # E. Unmatched detection.
    unmatched = detect_all_unmatched(billing, deployment, incident)
    ub, ud, ui = unmatched
    _write_csv(ub, UNMATCHED_BILLING_FILE)
    _write_csv(ud, UNMATCHED_DEPLOY_FILE)
    _write_csv(ui, UNMATCHED_INCIDENT_FILE)
    print(f"\nUnmatched -> billing:{len(ub)} deployments:{len(ud)} incidents:{len(ui)}")

    # F. Final analytical dataset.
    final = build_final_dataset(billing, deployment, incident)
    _write_csv(final, FINAL_DATASET_FILE)
    print(f"Final dataset ({len(final)} rows) -> {FINAL_DATASET_FILE}")

    # G. Validate merged output.
    merge_validation = validate_merged(final, billing)
    print("\nMerged validation:")
    for k, v in merge_validation.items():
        print(f"  {k}: {v}")

    # Documentation.
    write_merge_summary(MERGE_SUMMARY_FILE, key_findings, join_report,
                        unmatched, merge_validation)
    print(f"\nSummary -> {MERGE_SUMMARY_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
