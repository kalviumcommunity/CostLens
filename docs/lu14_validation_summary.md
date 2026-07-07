# LU-14 :: Data Consistency & Validation Summary

_Generated: 2026-07-07T10:06:12.383365+00:00_

## Overview

- **Total Records:** 20
- **Valid Records:** 10 (50.0%)
- **Invalid Records:** 10 (50.0%)

## Validation Results

| Rule | Passed | Failed | Pass % |
| --- | ---: | ---: | ---: |
| Rule 1 - Cost >= 0 | 18 | 2 | 90.0% |
| Rule 2 - CPU Utilization in [0,100] | 18 | 2 | 90.0% |
| Rule 3 - Memory Utilization in [0,100] | 19 | 1 | 95.0% |
| Rule 4 - Deployment Date <= Incident Date | 19 | 1 | 95.0% |
| Rule 5 - Project_ID exists in projects | 18 | 2 | 90.0% |
| Rule 6 - No nulls in key columns | 18 | 2 | 90.0% |
| Rule 7 - Cloud Provider in {AWS,Azure,GCP} | 19 | 1 | 95.0% |

## Top Validation Failures

- **Rule 1 - Cost >= 0** — 2 failing row(s)
- **Rule 2 - CPU Utilization in [0,100]** — 2 failing row(s)
- **Rule 5 - Project_ID exists in projects** — 2 failing row(s)
- **Rule 6 - No nulls in key columns** — 2 failing row(s)
- **Rule 3 - Memory Utilization in [0,100]** — 1 failing row(s)
- **Rule 4 - Deployment Date <= Incident Date** — 1 failing row(s)
- **Rule 7 - Cloud Provider in {AWS,Azure,GCP}** — 1 failing row(s)

## Recommendations

- Investigate negative/missing costs; check refund & sign handling in the ingestion job.
- Clamp or re-source CPU metrics; confirm the collector emits a 0-100 percentage.
- Backfill missing projects into the reference table or drop orphan deployments.
- Enforce NOT NULL on key columns at the source before ingestion.
- Clamp or re-source Memory metrics; confirm the collector emits a 0-100 percentage.
- Fix event ordering; deployment must precede or equal the incident timestamp.
- Standardise provider names to {AWS, Azure, GCP} or add explicit support.
- Re-run validation after remediation; block promotion until pass rate meets SLA.
