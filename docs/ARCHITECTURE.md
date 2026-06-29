# 🏛️ System Architecture Specification

## CostLens AI — Platform Systems Architecture

---

| Field             | Detail                                           |
| ----------------- | ------------------------------------------------ |
| **Document ID**   | CLAI-ARCH-001                                    |
| **Version**       | 1.0.0                                            |
| **Status**        | Approved                                         |
| **Created**       | 2026-06-29                                       |
| **Last Updated**  | 2026-06-29                                       |
| **Document Type** | Systems & Pipeline Architecture Specification    |
| **Project**       | CostLens AI                                      |
| **Tech Stack**    | SQLite / Postgres · Pandas · Streamlit · GitHub Actions |

---

## 1. System Overview & High-Level Design

CostLens AI is structured as a modular Data Product designed to clean, enrich, model, and serve cloud cost context. The architecture isolates ingestion logic, transformation pipelines, SQL storage, ML training, and UI components to ensure clean execution and testability.

```
       +--------------------------------------------------------+
       |                  DATA SOURCES (CSV/JSON)               |
       |  [Billing Data] [Usage Metrics] [Deployments] [Teams]  |
       +---------------------------+----------------------------+
                                   |
                                   v (Pipeline Runner)
       +--------------------------------------------------------+
       |                INGESTION & CLEANING LAYER              |
       |  - Schema Validation (Pandas)                          |
       |  - Deduping & Type Casting                             |
       +---------------------------+----------------------------+
                                   |
                                   v
       +--------------------------------------------------------+
       |                 DATA STORAGE LAYER (SQL)               |
       |  - Unified Fact / Dimension Schema                     |
       |  - Normalized database views                           |
       +---------------------+-----+----------------------------+
                             |     |
            +----------------+     +---------------+
            |                                      |
            v                                      v
+-----------------------+              +------------------------+
|   ANALYTICS ENGINE    |              |       ML LAYER         |
|  - SQL Query Engine   |              |  - Isolation Forest    |
|  - Unit Cost Metrics  |              |  - Linear/RF Forecast  |
+-----------+-----------+              +-----------+------------+
            |                                      |
            +----------------+     +---------------+
                             |     |
                             v     v
       +--------------------------------------------------------+
       |               STREAMLIT PRESENTATION LAYER             |
       |  - Executive Dashboard View                            |
       |  - Engineering Regression Tracing                      |
       |  - FinOps Anomaly Drilldown & Right-sizing             |
       +--------------------------------------------------------+
```

---

## 2. Ingestion & Storage Strategy

- **Raw Ingestion:** Python modules (`src/ingestion/`) ingest file objects, validate boundaries and mandatory columns, and cast types to ensure data consistency.
- **Relational Storage:** Data is stored in SQLite for local development and PostgreSQL for deployment. Key joins (e.g., matching usage and deployments to billing events) are pre-calculated using indexed tables.

---

## 3. Machine Learning (Anomaly & Forecasting) Pipeline

The ML pipeline is divided into two distinct training processes:

```
[Processed Fact Billing]
        |
        +------> [Isolation Forest (Unsupervised)] ──> Anomaly Flag Output
        |
        +------> [Scikit-Learn Regressors]         ──> 7/30-Day Cost Forecasts
```

- **Anomaly Detection Engine:** Applies an `Isolation Forest` model over daily service costs, usage volumes, and environment types to detect outliers.
- **Forecasting Engine:** Evaluates running window shifts over time-series billing data, using Lag Features to project upcoming budget trends.

---

## 4. CI/CD Pipeline & GitHub Workflow

GitHub Actions serves as the automation layer for the platform:

```
[Developer Push] ──> [Linter (Flake8)] ──> [Unit Tests (Pytest)] ──> [Schema Check] ──> [Success/Block Merge]
```

Every pull request to `main` triggers a series of checks:
1. **Quality Checks:** Runs code style checks (`flake8`).
2. **Unit Tests:** Executes code logic tests (`pytest`).
3. **Pipeline Verifications:** Runs mock pipeline executions to verify that schema updates do not break ingestion or model training.

---

## 5. Security & Scaling Strategy

- **Secret Isolation:** Environment variables are loaded at runtime from `.env` files. Secrets are never checked into git.
- **Cache Optimization:** Uses Streamlit caching mechanisms (`@st.cache_data`) for SQL query results to keep page loads under 3 seconds.
- **Future Scale Plan:** Outlines migrations to cloud data warehouses (e.g., Snowflake, BigQuery) for enterprise workloads.
