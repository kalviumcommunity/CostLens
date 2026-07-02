"""
LU-07 :: Data Dictionary & Business Context Mapping
===================================================

Translates the technical schema of the cloud cost dataset into business
meaning, operational context, KPIs and stakeholder-friendly definitions.

The script:
    1. Reads the dataset schema automatically (column name, dtype, sample).
    2. Builds a per-column data dictionary (description + business meaning).
    3. Maps columns to business KPIs and explains why each matters.
    4. Flags ambiguous columns that could be misunderstood.
    5. Documents business relationships between columns.
    6. Exports a Markdown dictionary (docs/data_dictionary.md) and a
       machine-readable CSV (outputs/data_dictionary.csv).

Run:
    python scripts/generate_data_dictionary.py
"""

from __future__ import annotations

import csv
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration: input dataset and output targets.
# ---------------------------------------------------------------------------
INPUT_FILE = os.path.join("data", "raw", "cloud_costs.csv")
DOCS_DIR = "docs"
OUTPUT_DIR = "outputs"
DICTIONARY_MD = os.path.join(DOCS_DIR, "data_dictionary.md")
DICTIONARY_CSV = os.path.join(OUTPUT_DIR, "data_dictionary.csv")

# ---------------------------------------------------------------------------
# Business knowledge base: human-authored context keyed by column name.
# Description  = what the column technically holds.
# business     = why it matters operationally / who consumes it.
# ---------------------------------------------------------------------------
BUSINESS_CONTEXT: dict[str, dict[str, str]] = {
    "timestamp": {
        "description": "Date and time (ISO 8601, UTC) the cost record was "
                       "captured for a billing interval.",
        "business": "Anchors every cost to a point in time, enabling daily / "
                    "monthly trend analysis and anomaly detection by Finance "
                    "and Engineering.",
    },
    "service_name": {
        "description": "Name of the cloud service that generated the charge "
                       "(e.g. Compute Engine, BigQuery, Cloud Storage).",
        "business": "Attributes spend to a specific managed service so teams "
                    "can see which products drive the bill and target "
                    "optimisation.",
    },
    "environment": {
        "description": "Deployment environment the cost belongs to "
                       "(Production, Staging, Development).",
        "business": "Allocates spend across environments so non-production "
                    "waste is visible and Production reliability spend is "
                    "justified.",
    },
    "cost_usd": {
        "description": "Cloud infrastructure cost in US dollars for the "
                       "service and interval on this record.",
        "business": "Represents operational spending tracked by Finance and "
                    "Engineering teams; the core measure for budgets, "
                    "forecasts and cost KPIs.",
    },
    "deployment_id": {
        "description": "Unique identifier for the infrastructure deployment "
                       "event associated with the cost.",
        "business": "Links cloud spend back to a specific deployment so cost "
                    "spikes can be traced to the change that caused them "
                    "(root cause analysis).",
    },
}

# ---------------------------------------------------------------------------
# KPI mapping: column -> (KPI name, why it matters).
# ---------------------------------------------------------------------------
KPI_MAPPING: dict[str, dict[str, str]] = {
    "cost_usd": {
        "kpi": "Monthly Cloud Cost KPI",
        "why": "Primary financial metric; tracks total spend against budget "
               "and drives forecasting and cost-control decisions.",
    },
    "timestamp": {
        "kpi": "Daily Cost Trend KPI",
        "why": "Reveals day-over-day spend movement so sudden increases are "
               "caught early before they compound into budget overruns.",
    },
    "deployment_id": {
        "kpi": "Deployment Tracking KPI",
        "why": "Ties cost to deployment events, enabling root cause analysis "
               "of cost spikes and accountability per release.",
    },
    "environment": {
        "kpi": "Environment Cost Allocation KPI",
        "why": "Splits spend across Production, Staging and Development to "
               "expose non-production waste and right-size lower environments.",
    },
    "service_name": {
        "kpi": "Service Cost Attribution KPI",
        "why": "Attributes spend to individual cloud services so the most "
               "expensive services can be prioritised for optimisation.",
    },
}

# ---------------------------------------------------------------------------
# Ambiguous column assessment: columns easily misread by stakeholders.
# ---------------------------------------------------------------------------
AMBIGUOUS_COLUMNS: list[dict[str, str]] = [
    {
        "column": "deployment_id",
        "possible": "Application release / version ID owned by the app team.",
        "business": "Unique identifier for an infrastructure deployment event, "
                    "not a semantic app version.",
        "reasoning": "'Deployment' overlaps with software release language; "
                     "here it identifies the infra provisioning event that a "
                     "cost is billed against, so a single ID can span multiple "
                     "services and dates.",
    },
    {
        "column": "cost_usd",
        "possible": "Total invoiced amount for the whole account or month.",
        "business": "Cost for a single service during one billing interval; "
                    "totals are an aggregation of many rows.",
        "reasoning": "Readers may assume one row equals the full bill. Each "
                     "row is a granular slice, so cost must be summed across "
                     "rows to reach an account or monthly total.",
    },
    {
        "column": "environment",
        "possible": "The cloud region or data-centre location.",
        "business": "The software lifecycle stage (Production / Staging / "
                    "Development), unrelated to geography.",
        "reasoning": "'Environment' is overloaded and can suggest region or "
                     "runtime. Here it strictly means lifecycle stage and "
                     "needs normalisation (casing/whitespace) before "
                     "allocation.",
    },
]

# ---------------------------------------------------------------------------
# Business relationships between columns.
# ---------------------------------------------------------------------------
RELATIONSHIPS: list[dict[str, str]] = [
    {
        "pair": "deployment_id \u2194 cost_usd",
        "business": "Measures the infrastructure cost generated by a specific "
                    "deployment, enabling per-deployment cost attribution and "
                    "root cause analysis of spikes.",
    },
    {
        "pair": "environment \u2194 cost_usd",
        "business": "Measures spending differences across Production, Staging "
                    "and Development, exposing where non-production waste "
                    "occurs.",
    },
    {
        "pair": "service_name \u2194 cost_usd",
        "business": "Measures how much each cloud service contributes to total "
                    "spend, guiding service-level optimisation priorities.",
    },
    {
        "pair": "timestamp \u2194 cost_usd",
        "business": "Measures how spend evolves over time, powering daily and "
                    "monthly cost trend KPIs.",
    },
]


# ---------------------------------------------------------------------------
# load_dataset(): read the raw CSV.
# ---------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load the dataset whose schema will be documented."""
    return pd.read_csv(path, encoding="utf-8", delimiter=",")


# ---------------------------------------------------------------------------
# extract_schema(): read column name, dtype and a representative sample value.
# ---------------------------------------------------------------------------
def extract_schema(df: pd.DataFrame) -> list[dict[str, str]]:
    """Automatically capture name, data type and sample value per column."""
    schema: list[dict[str, str]] = []
    for col in df.columns:
        # First non-null value keeps the sample meaningful (skips blanks).
        non_null = df[col].dropna()
        sample = non_null.iloc[0] if not non_null.empty else ""
        schema.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "sample": str(sample).strip(),
        })
    return schema


# ---------------------------------------------------------------------------
# build_dictionary(): merge auto-detected schema with business context.
# ---------------------------------------------------------------------------
def build_dictionary(schema: list[dict[str, str]]) -> list[dict[str, str]]:
    """Combine schema and business knowledge into dictionary rows."""
    rows: list[dict[str, str]] = []
    for entry in schema:
        col = entry["column"]
        ctx = BUSINESS_CONTEXT.get(col, {
            "description": "No business description defined for this column.",
            "business": "Pending stakeholder review.",
        })
        rows.append({
            "column": col,
            "dtype": entry["dtype"],
            "description": ctx["description"],
            "sample": entry["sample"],
            "business": ctx["business"],
        })
    return rows


# ---------------------------------------------------------------------------
# write_markdown(): render the full data dictionary document.
# ---------------------------------------------------------------------------
def write_markdown(rows: list[dict[str, str]]) -> None:
    """Write docs/data_dictionary.md with all required sections."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    lines: list[str] = []

    lines.append("# Data Dictionary — Cloud Cost Intelligence Platform\n")
    lines.append("_Auto-generated by `scripts/generate_data_dictionary.py`._\n")
    lines.append(
        "This dictionary translates the technical schema of "
        "`data/raw/cloud_costs.csv` into business meaning, KPIs and "
        "stakeholder-friendly definitions.\n"
    )

    # --- Section 1: Column dictionary table ---
    lines.append("## Column Dictionary\n")
    lines.append(
        "| Column Name | Data Type | Description | Example Value | "
        "Business Meaning |"
    )
    lines.append(
        "| ----------- | --------- | ----------- | ------------- | "
        "---------------- |"
    )
    for r in rows:
        lines.append(
            f"| {r['column']} | {r['dtype']} | {r['description']} | "
            f"{r['sample']} | {r['business']} |"
        )
    lines.append("")

    # --- Section 2: Business KPI mapping ---
    lines.append("## Business KPI Mapping\n")
    lines.append(
        "Each column below powers a business KPI. Understanding why each KPI "
        "matters keeps analytics aligned with financial and engineering "
        "goals.\n"
    )
    lines.append("| Column | Mapped KPI | Why It Matters |")
    lines.append("| ------ | ---------- | -------------- |")
    for col, m in KPI_MAPPING.items():
        lines.append(f"| {col} | {m['kpi']} | {m['why']} |")
    lines.append("")

    # --- Section 3: Ambiguous column assessment ---
    lines.append("## Ambiguous Column Assessment\n")
    lines.append(
        "Columns that stakeholders could misinterpret, with the intended "
        "business definition and reasoning.\n"
    )
    for a in AMBIGUOUS_COLUMNS:
        lines.append(f"### {a['column']}\n")
        lines.append(f"- **Possible Interpretation:** {a['possible']}")
        lines.append(f"- **Business Interpretation:** {a['business']}")
        lines.append(f"- **Reasoning:** {a['reasoning']}\n")

    # --- Section 4: Business relationships ---
    lines.append("## Business Relationships\n")
    lines.append(
        "How columns relate to one another and what the relationship measures "
        "for the business.\n"
    )
    for i, rel in enumerate(RELATIONSHIPS, start=1):
        lines.append(f"### Relationship {i}\n")
        lines.append(f"**{rel['pair']}**\n")
        lines.append(f"Business Meaning: {rel['business']}\n")

    with open(DICTIONARY_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# ---------------------------------------------------------------------------
# write_csv(): export the column dictionary as a flat CSV.
# ---------------------------------------------------------------------------
def write_csv(rows: list[dict[str, str]]) -> None:
    """Write outputs/data_dictionary.csv for programmatic consumers."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fieldnames = [
        "column_name", "data_type", "description",
        "example_value", "business_meaning",
    ]
    with open(DICTIONARY_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "column_name": r["column"],
                "data_type": r["dtype"],
                "description": r["description"],
                "example_value": r["sample"],
                "business_meaning": r["business"],
            })


# ---------------------------------------------------------------------------
# Terminal summary
# ---------------------------------------------------------------------------
def print_summary(rows: list[dict[str, str]]) -> None:
    """Print a concise summary of the generated dictionary."""
    print("=" * 40)
    print("DATA DICTIONARY SUMMARY")
    print("=" * 40)
    print(f"Columns documented : {len(rows)}")
    print(f"KPIs mapped        : {len(KPI_MAPPING)}")
    print(f"Ambiguous columns  : {len(AMBIGUOUS_COLUMNS)}")
    print(f"Relationships      : {len(RELATIONSHIPS)}")
    for r in rows:
        print(f"  - {r['column']} ({r['dtype']})")


def main() -> None:
    df = load_dataset(INPUT_FILE)
    schema = extract_schema(df)
    rows = build_dictionary(schema)
    write_markdown(rows)
    write_csv(rows)
    print_summary(rows)
    print(f"\nGenerated:\n  {DICTIONARY_MD}\n  {DICTIONARY_CSV}")


if __name__ == "__main__":
    main()
