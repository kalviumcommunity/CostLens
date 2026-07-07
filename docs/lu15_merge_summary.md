# LU-15 :: Multi-Source Merging & Join Validation Summary

_Generated: 2026-07-07T10:16:46.729120+00:00_

## Why Each Join Type Exists

- **INNER JOIN** — keeps only projects present in *both* sources. Use when analysis requires complete billing **and** deployment context (e.g. cost-per-deployment). Trades coverage for completeness.
- **LEFT JOIN** — keeps every billing row, enriches with deployment data where it exists. Preserves 100% of spend; unmatched context is NULL.
- **OUTER JOIN** — keeps every row from *both* sources, matched or not. Best for auditing/reconciliation to surface orphans on either side.

## Why LEFT JOIN Was Selected for the Final Dataset

Billing is the **source of financial truth** — every dollar of spend must survive the merge. A LEFT JOIN anchored on `billing_data` guarantees no cost row is dropped, while deployment and incident data enrich rows that have matches and stay NULL where they do not. An INNER JOIN would silently discard spend for projects lacking a deployment/incident record, under-reporting total cost.

## Business Reasoning

- Under-counting spend is unacceptable for FinOps reporting -> never drop billing rows.
- Missing deployment/incident context is acceptable and explicitly modelled as NULL.
- Orphan keys are surfaced (not hidden) so data owners can backfill sources.

## Join Key Findings

| Dataset | Rows | Unique Keys | Null Keys | Duplicate-Key Rows |
| --- | ---: | ---: | ---: | ---: |
| billing_data | 10 | 8 | 1 | 2 |
| deployment_history | 8 | 7 | 1 | 0 |
| incident_logs | 7 | 6 | 0 | 2 |

## Join Validation Results (billing + deployment_history)

| Join Type | Rows Before | Rows After | Rows Added | Rows Lost |
| --- | ---: | ---: | ---: | ---: |
| INNER | 10 | 7 | 0 | 3 |
| LEFT | 10 | 10 | 0 | 0 |
| OUTER | 10 | 12 | 2 | 0 |

## Unmatched Key Findings

- **billing_data only:** 2 row(s) — projects `['PRJ007', 'PRJ009']`
- **deployment_history only:** 2 row(s) — projects `['PRJ008', 'PRJ010']`
- **incident_logs only:** 1 row(s) — projects `['PRJ011']`

## Merged Dataset Validation

- Final rows: **12**
- Duplicate columns: `none`
- Rows with duplicate Project_ID (expected fan-out): **4**
- Key conflicts (billing keys lost in merge): `none`
- Null audit (col -> null count): `{'Project_ID': 1, 'Deployment_ID': 3, 'Deployment_Date': 3, 'Deployment_Type': 3, 'Incident_ID': 4, 'Incident_Date': 4, 'Severity': 4}`

## Recommendations

- Backfill orphan projects into the missing source(s) or tag them as out-of-scope so reconciliation stays clean.
- Enforce NOT NULL on `Project_ID` at ingestion for all three sources.
- Treat duplicate-key fan-out explicitly: pre-aggregate billing to project grain before merging if a 1-row-per-project analytical grain is required.
- Re-run this validation on every data refresh; block promotion if billing rows are lost or unexpected duplicate columns appear.

