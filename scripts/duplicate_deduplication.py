"""
LU-10 :: Duplicate Detection & Record Deduplication
===================================================

Detects both EXACT and NEAR duplicate records in the standardised cloud cost
dataset and removes them safely while keeping an audit trail.

Two kinds of duplicates:
    * Exact duplicate  - every column is identical (a full-row copy).
    * Near duplicate    - the same logical entity (same KEY_COLUMNS) appears more
                          than once with differing details (e.g. an updated cost
                          or a later billing date).

Deduplication policy (explicit):
    * Exact duplicates -> keep the FIRST occurrence (`keep="first"`).
    * Near duplicates  -> keep the MOST COMPLETE record per entity (fewest nulls);
                          ties broken by the MOST RECENT Billing_Date.

Every removed record is written to a separate audit log, and row counts before
and after are compared. The input dataset is read-only; the deduplicated result
is saved to a new file.

Run:
    python scripts/duplicate_deduplication.py
"""

from __future__ import annotations

import os

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration: input (read-only) and output targets.
# ---------------------------------------------------------------------------
INPUT_FILE = os.path.join(
    "data", "processed", "cloud_cost_dataset_standardized.csv"
)
DEDUP_FILE = os.path.join(
    "data", "processed", "cloud_cost_dataset_deduplicated.csv"
)
REPORTS_DIR = "reports"
REMOVED_LOG_CSV = os.path.join(REPORTS_DIR, "removed_duplicates.csv")
SUMMARY_MD = os.path.join(REPORTS_DIR, "deduplication_summary.md")

# ---------------------------------------------------------------------------
# KEY_COLUMNS: the column combination that identifies a single logical entity.
# A cloud deployment is uniquely identified by its Deployment_ID, so repeated
# IDs (with differing details) are treated as near-duplicates of one entity.
# ---------------------------------------------------------------------------
KEY_COLUMNS = ["Deployment_ID"]

# Column used to break completeness ties (most recent record wins).
RECENCY_COLUMN = "Billing_Date"


# ---------------------------------------------------------------------------
# load_dataset(): read the standardised CSV (read-only source).
# ---------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load the standardised dataset to deduplicate."""
    return pd.read_csv(path, encoding="utf-8")


# ---------------------------------------------------------------------------
# detect_exact_duplicates(): flag full-row duplicates via .duplicated().
# ---------------------------------------------------------------------------
def detect_exact_duplicates(df: pd.DataFrame) -> pd.Series:
    """Return a boolean mask of exact duplicate rows (keep='first').

    `keep="first"` marks every occurrence AFTER the first as a duplicate, so the
    first record is retained and the copies are flagged for removal.
    """
    return df.duplicated(keep="first")


# ---------------------------------------------------------------------------
# completeness_score(): count of non-null fields per row (higher = better).
# ---------------------------------------------------------------------------
def completeness_score(df: pd.DataFrame) -> pd.Series:
    """Score each row by how many columns are populated (non-null)."""
    return df.notna().sum(axis=1)


# ---------------------------------------------------------------------------
# deduplicate(): remove exact then near duplicates, returning kept + removed.
# ---------------------------------------------------------------------------
def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Run the two-stage dedup and return (kept_df, removed_df, stats)."""
    removed_frames: list[pd.DataFrame] = []
    stats: dict[str, int] = {"rows_before": len(df)}

    # --- STAGE 1: exact duplicates (full-row copies) ---
    exact_mask = detect_exact_duplicates(df)
    exact_count = int(exact_mask.sum())
    stats["exact_duplicates"] = exact_count

    if exact_count:
        removed_exact = df[exact_mask].copy()
        removed_exact["duplicate_type"] = "exact"
        removed_exact["removal_reason"] = "Full-row duplicate; kept first occurrence"
        removed_frames.append(removed_exact)

    # Keep only the first occurrence of each exact duplicate.
    working = df[~exact_mask].copy()

    # --- STAGE 2: near duplicates (same entity, differing details) ---
    # Rank records within each entity group: most complete first, then most
    # recent Billing_Date. The top-ranked record per group is kept.
    working["_completeness"] = completeness_score(
        working.drop(columns=[c for c in ["_completeness"] if c in working])
    )

    # Recency key (parsed as datetime; unparseable/missing sort last).
    if RECENCY_COLUMN in working.columns:
        working["_recency"] = pd.to_datetime(
            working[RECENCY_COLUMN], errors="coerce"
        )
    else:
        working["_recency"] = pd.NaT

    # Sort so the preferred record (highest completeness, then most recent)
    # is first within each entity group.
    working_sorted = working.sort_values(
        by=["_completeness", "_recency"],
        ascending=[False, False],
    )

    # Mark near-duplicates: any repeat of the same KEY_COLUMNS after the first
    # (which is now the preferred record thanks to the sort above).
    near_mask = working_sorted.duplicated(subset=KEY_COLUMNS, keep="first")
    near_count = int(near_mask.sum())
    stats["near_duplicates"] = near_count

    if near_count:
        removed_near = working_sorted[near_mask].drop(
            columns=["_completeness", "_recency"]
        ).copy()
        removed_near["duplicate_type"] = "near"
        removed_near["removal_reason"] = (
            f"Duplicate {'+'.join(KEY_COLUMNS)}; kept most complete/recent record"
        )
        removed_frames.append(removed_near)

    # Kept records: preferred record per entity, restored to original order.
    kept = (
        working_sorted[~near_mask]
        .drop(columns=["_completeness", "_recency"])
        .sort_index()
    )

    stats["rows_after"] = len(kept)
    stats["rows_removed"] = stats["rows_before"] - stats["rows_after"]

    removed = (
        pd.concat(removed_frames, ignore_index=True)
        if removed_frames
        else pd.DataFrame(columns=list(df.columns) + ["duplicate_type", "removal_reason"])
    )
    return kept, removed, stats


# ---------------------------------------------------------------------------
# save_outputs(): write dedup dataset, removed-record log and summary.
# ---------------------------------------------------------------------------
def save_outputs(
    kept: pd.DataFrame, removed: pd.DataFrame, stats: dict
) -> None:
    """Persist the deduplicated dataset, audit log and summary report."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DEDUP_FILE), exist_ok=True)

    # Deduplicated dataset (input file left untouched).
    kept.to_csv(DEDUP_FILE, index=False)

    # Audit log of every removed record.
    removed.to_csv(REMOVED_LOG_CSV, index=False)

    # Row-count comparison + policy documentation.
    lines = ["# Deduplication Summary — LU-10\n"]
    lines.append("## Row Count Comparison\n")
    lines.append("| Metric | Value |")
    lines.append("| ------ | ----- |")
    lines.append(f"| Rows before | {stats['rows_before']} |")
    lines.append(f"| Exact duplicates removed | {stats['exact_duplicates']} |")
    lines.append(f"| Near duplicates removed | {stats['near_duplicates']} |")
    lines.append(f"| Total rows removed | {stats['rows_removed']} |")
    lines.append(f"| Rows after | {stats['rows_after']} |\n")

    lines.append("## Deduplication Policy\n")
    lines.append(
        f"- **Entity key (near-duplicates):** `{', '.join(KEY_COLUMNS)}`"
    )
    lines.append(
        "- **Exact duplicates:** detected with `df.duplicated(keep=\"first\")`; "
        "the first occurrence is kept."
    )
    lines.append(
        "- **Near duplicates:** per entity, keep the **most complete** record "
        f"(fewest nulls); ties broken by the most recent `{RECENCY_COLUMN}`."
    )
    lines.append(
        "- **Audit trail:** every removed record is logged to "
        f"`{REMOVED_LOG_CSV}` with its duplicate type and removal reason.\n"
    )

    with open(SUMMARY_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    # Load standardised dataset (read-only).
    df = load_dataset(INPUT_FILE)

    # Log exact duplicate count BEFORE removal (rubric requirement).
    exact_before = int(df.duplicated(keep="first").sum())
    print("=" * 60)
    print("DUPLICATE DETECTION")
    print("=" * 60)
    print(f"Rows before deduplication : {len(df)}")
    print(f"Exact duplicates detected : {exact_before}")

    # Run two-stage deduplication.
    kept, removed, stats = deduplicate(df)

    print(f"Near duplicates detected  : {stats['near_duplicates']} "
          f"(entity key: {', '.join(KEY_COLUMNS)})")
    print(f"Total records removed     : {stats['rows_removed']}")
    print(f"Rows after deduplication  : {stats['rows_after']}")
    print()

    if not removed.empty:
        print("Removed records:")
        cols = KEY_COLUMNS + ["duplicate_type", "removal_reason"]
        print(removed[cols].to_string(index=False))
        print()

    # Save dataset, audit log and summary.
    save_outputs(kept, removed, stats)

    print("Generated:")
    for path in (DEDUP_FILE, REMOVED_LOG_CSV, SUMMARY_MD):
        print(f"  {path}")
    print(f"\nInput dataset untouched: {INPUT_FILE}")


if __name__ == "__main__":
    main()
