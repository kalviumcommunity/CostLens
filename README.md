<div align="center">

# ☁️ CostLens AI

### *Cloud Cost Intelligence & Root Cause Analysis*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

> **Understand. Attribute. Predict. Optimize.**

*An AI-powered platform that tells you not just **how much** you're spending on cloud — but exactly **why**, **who caused it**, and **what to do next**.*

</div>

---

## 🔍 The Problem

Cloud bills are hard to explain.

By the time finance notices a spike, the cause is already days old. Engineering teams don't know which deployment triggered the increase. Finance teams can't attribute costs to specific teams. Everyone is reactive — nobody is proactive.

**CostLens AI changes that.**

---

## ✨ What It Does

| Capability | Description |
|---|---|
| 📊 **Cost Visibility** | Breakdown of spending by service, team, environment & time |
| 🔎 **Root Cause Analysis** | Links cost spikes to specific deployments and services |
| 🚨 **Anomaly Detection** | Automatically flags unusual spending patterns |
| 🔮 **Predictive Forecasting** | Predicts next week, next month, and budget overrun risk |
| 💡 **Optimization Insights** | Surfaces actionable recommendations to reduce waste |
| 📋 **Executive Reporting** | Clean, business-friendly dashboards for decision makers |

---

## 🧠 How It Works

```
Raw Cloud Data  ──►  Data Processing  ──►  Analytics Engine  ──►  ML Models  ──►  Dashboard
  (Billing,              (Pandas,              (SQL + KPIs)         (Forecasting      (Streamlit)
   Usage,                NumPy,                                      + Anomaly
   Deployments,          SQLite)                                     Detection)
   Teams)
```

1. **Ingest** — Pull billing, usage, deployment, and ownership data
2. **Process** — Clean, join, and structure the datasets
3. **Analyze** — Run SQL-powered KPI queries and EDA
4. **Model** — Forecast costs & detect anomalies with ML
5. **Visualize** — Surface insights via an interactive Streamlit dashboard

---

## 🗂️ Repository Structure

```
costlens/
│
├── 📁 data/
│   ├── raw/              # Original source datasets
│   └── processed/        # Cleaned & transformed data
│
├── 📁 notebooks/         # Exploratory analysis & prototyping
│
├── 📁 src/
│   ├── ingestion/        # Data loading & connectors
│   ├── cleaning/         # Preprocessing pipelines
│   ├── analytics/        # KPI computation & EDA
│   ├── models/           # ML models (forecasting, anomaly detection)
│   └── dashboard/        # Streamlit app components
│
├── 📁 sql/               # SQL queries for cost analysis
│
├── 📁 reports/           # Generated reports & summaries
│
├── 📁 screenshots/       # Dashboard previews
│
├── 📁 .github/           # CI/CD workflows
│
├── app.py                # Main Streamlit entry point
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🤖 Machine Learning

### Cost Forecasting
Predicts upcoming cloud spend using historical billing patterns.
- `Linear Regression` — baseline trend modeling
- `Random Forest` — non-linear pattern recognition
- `XGBoost` *(optional)* — high-accuracy ensemble forecasting

### Anomaly Detection
Flags unexpected spikes before they escalate.
- `Isolation Forest` — unsupervised outlier detection
- `Z-Score Analysis` — statistical deviation tracking
- `IQR Method` — robust threshold-based detection

---

## 📈 Dashboard Views

**🏢 Executive View** — Total spend, budget utilization, forecasted cost, monthly trend

**⚙️ Engineering View** — Cost by service, deployment impact, resource consumption

**💰 FinOps View** — Cost attribution, anomalies, optimization suggestions, budget risk

**🔥 AI Insights** — Natural language summaries like:
> *"Costs increased 18% over 7 days. Primary driver: Recommendation Service (Deployment v3.4). Estimated monthly impact: +$2,400."*

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Database | PostgreSQL / SQLite |
| Analytics | SQL |
| Machine Learning | Scikit-learn, XGBoost |
| Dashboard | Streamlit |
| BI Reporting | Power BI |
| CI/CD | GitHub Actions |

---

## Team Workflow

Issue
↓
Feature Branch
↓
Development
↓
Pull Request
↓
Review
↓
Merge

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/kalviumcommunity/CostLens.git
cd CostLens

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```


## 📖 LU-07 Data Dictionary & Business Context Mapping

### Objective

Translate the technical schema of `data/raw/cloud_costs.csv` into business
meaning, operational context, KPIs and stakeholder-friendly definitions so
Finance and Engineering share one language for cloud spend.

### Business Context Workflow

1. **Read schema automatically** — `extract_schema()` captures each column's
   name, data type and a representative sample value.
2. **Map business context** — merge the schema with a human-authored
   knowledge base (description + business meaning) into dictionary rows.
3. **Attach KPIs** — link each column to the business KPI it powers.
4. **Flag ambiguity** — surface columns stakeholders could misread.
5. **Document relationships** — describe how columns relate for the business.
6. **Export** — write `docs/data_dictionary.md` and
   `outputs/data_dictionary.csv`.

### KPI Mapping

| Column | Mapped KPI |
|---|---|
| cost_usd | Monthly Cloud Cost KPI |
| timestamp | Daily Cost Trend KPI |
| deployment_id | Deployment Tracking KPI |
| environment | Environment Cost Allocation KPI |
| service_name | Service Cost Attribution KPI |

Each KPI keeps analytics aligned with budgeting, trend detection, release
accountability, environment allocation and service-level optimisation.

### Ambiguous Field Analysis

- **deployment_id** — read as an app release ID; actually the infrastructure
  deployment event a cost is billed against.
- **cost_usd** — read as the full invoice; actually one service/interval slice
  that must be summed for totals.
- **environment** — read as a cloud region; actually the software lifecycle
  stage (Production / Staging / Development).

### Relationship Mapping

- `deployment_id ↔ cost_usd` — infrastructure cost per deployment (root cause).
- `environment ↔ cost_usd` — spend differences across environments.
- `service_name ↔ cost_usd` — each service's contribution to total spend.
- `timestamp ↔ cost_usd` — spend evolution over time (trend KPIs).

### Run

```bash
python scripts/generate_data_dictionary.py
```

### Generated Outputs

- `docs/data_dictionary.md` — full business data dictionary
- `outputs/data_dictionary.csv` — machine-readable column dictionary
- **Script:** `scripts/generate_data_dictionary.py`

---

## 🧩 LU08 Missing Value Detection & Imputation

### Problem

Real cloud billing exports arrive with gaps: missing costs, unlabelled teams,
blank environments and absent cost centers. Left unhandled, these nulls break
aggregations and skew KPIs. This unit detects missing values, imputes them with
business-aware strategies, and preserves the raw source untouched.

### Missing Value Report

`missing_value_imputation.py` prints a per-column report of **Column Name,
Data Type, Null Count and Null Percentage** for `data/raw/cloud_cost_dataset.csv`.

### Imputation Strategy

| Column(s) | Type | Method | Reason |
|---|---|---|---|
| Monthly_Cost, CPU_Usage | Numerical | Median | Robust to outliers vs mean |
| Team_Name, Environment | Categorical | Mode | Most frequent value as default |
| Deployment_Date | Time-series | Forward Fill | Carries last known date forward |
| Cost_Center | Business rule | Constant `"Unknown"` | Cannot guess; flag for finance |

Every decision (column, missing %, method, reason) is logged to
`reports/imputation_decisions.md`. A before/after null comparison is written to
`reports/null_comparison.csv`. The cleaned dataset is saved **separately** to
`data/processed/cloud_cost_dataset_cleaned.csv` — the raw file is never modified.

### Run

```bash
python scripts/missing_value_imputation.py
```

### Output Files

- `reports/imputation_decisions.md` — decision log
- `reports/null_comparison.csv` — nulls before vs after
- `data/processed/cloud_cost_dataset_cleaned.csv` — cleaned dataset
- **Script:** `scripts/missing_value_imputation.py`

---

## 🧮 LU09 Data Type Enforcement & Standardisation

### Problem

A cleaned dataset can still carry the wrong **types**: dates stored as text,
costs like `$1,240.50`, utilisation like `85%`, and flags as `0/1`. Analysis,
sorting and aggregation silently break until every column holds its correct
type. This unit audits and enforces types before analysis.

### Type Issues Found

| Column | Raw Form | Problem |
|---|---|---|
| Deployment_Date, Billing_Date | `2026-01-01`, `01/01/2026` | Dates stored as strings |
| Monthly_Cost | `$1,240.50`, `₹5600`, `€45.10` | Currency symbols + commas |
| CPU_Utilization | `85%` | Percent sign blocks numeric ops |
| Auto_Scaling_Enabled | `0` / `1` | Flags stored as text/int, not bool |
| Resource_Count | `8` | Counts stored as string |

### Conversion Logic

| Category | Method |
|---|---|
| Date | `pd.to_datetime(..., format=..., errors="coerce")` |
| Currency | strip `$ ₹ € £ ,` → `float` |
| Percentage | strip `%` → `float` |
| Boolean | map `0/1` → `bool` |
| Integer | `pd.to_numeric` → nullable `Int64` |

All conversions use `errors="coerce"`: unparseable values become `NaN`/`NaT`
and are logged to `reports/conversion_errors.csv` rather than crashing the run.
The input dataset is read-only; the result is saved separately.

### Run

```bash
python scripts/data_type_standardisation.py
```

### Output Reports

- `reports/dtype_before.csv` — column → current dtype
- `reports/dtype_after.csv` — column → updated dtype
- `reports/dtype_conversion_summary.csv` — before vs after
- `reports/conversion_errors.csv` — rows that failed conversion
- `data/processed/cloud_cost_dataset_standardized.csv` — standardised dataset
- **Script:** `scripts/data_type_standardisation.py`

### Key Learnings

- Explicit date `format` prevents ambiguous/silent misparsing.
- `errors="coerce"` + a failure log makes bad data visible, not fatal.
- Nullable `Int64` and real `bool` types unlock correct sorting, filtering
  and aggregation downstream.

---

## 🧹 LU10 Duplicate Detection & Record Deduplication

### Problem

Billing exports and merged sources introduce duplicate rows — both exact
copies and "near" duplicates (the same deployment re-ingested with an updated
cost or a later billing date). Blind removal risks deleting the *better* copy,
so we detect, choose which record to keep, and log everything removed.

### Exact vs Near Duplicates

- **Exact duplicate** — every column identical (a full-row copy).
  Detected with `df.duplicated(keep="first")`.
- **Near duplicate** — same logical entity (`Deployment_ID`) appearing more
  than once with differing details, e.g. `DEP015` with a missing cost vs the
  same ID with the cost populated.

### Deduplication Logic

| Stage | Rule |
|---|---|
| Exact | `df.duplicated(keep="first")` — keep the first occurrence |
| Near | Group by `Deployment_ID`; keep the **most complete** record (fewest nulls), ties broken by most recent `Billing_Date` |

The `keep` parameter controls which occurrence is *retained*: `"first"` keeps
the earliest, `"last"` keeps the latest, and `False` marks **all** duplicates.

### Audit Trail

Every removed record is written to `reports/removed_duplicates.csv` with its
`duplicate_type` (exact/near) and `removal_reason`. Row counts before and after
are documented in `reports/deduplication_summary.md`. The input dataset is never
modified — the result is saved to a new file.

### Run

```bash
python scripts/duplicate_deduplication.py
```

### Output Reports

- `reports/removed_duplicates.csv` — audit log of every removed record
- `reports/deduplication_summary.md` — before/after counts + policy
- `data/processed/cloud_cost_dataset_deduplicated.csv` — deduplicated dataset
- **Script:** `scripts/duplicate_deduplication.py`

### Key Learnings

- Exact dedup is a full-row match; near dedup needs a chosen **key column**
  combination that defines one entity.
- Choosing *which* record to keep (completeness/recency) matters more than the
  removal itself.
- Logging removed rows gives an auditable trail and prevents silent data loss.
- Slight spelling variations (e.g. `Prod` vs `Production`) need normalisation
  or fuzzy matching before key-based dedup will catch them.

---

## 🔤 LU11 String Cleaning & Text Normalisation

String fields are prone to human error, resulting in spelling variations, unwanted whitespaces, and inconsistent casing. This prevents precise grouping and filtering. This unit standardises text formatting across all string columns.

### Text Normalisation Steps

1. **Whitespace Cleaning**: `str.strip()` applied to remove leading/trailing spaces.
2. **Special Character Removal**: Unwanted characters (e.g. `@`, `#`, `$`, `%`, `&`, `*`, `!`) stripped via Regex.
3. **Case Normalisation**: `str.title()` enforced for consistent casing.
4. **Label Standardisation**: Known variants mapped to standard category names (e.g. `Aws` → `Amazon Web Services`).

### Run

```bash
python scripts/string_cleaning.py
```

### Output Reports

- `reports/string_columns_report.csv` — Datatype and unique values for each string column
- `reports/text_normalisation_examples.csv` — Sample showing values before vs after normalisation
- `reports/string_cleaning_summary.csv` — Quality summary of unique categories and changes
- `docs/text_normalisation_strategy.md` — Detailed normalisation rules and mapping strategy
- `data/processed/cloud_cost_dataset_text_cleaned.csv` — The fully cleaned dataset
- **Script:** `scripts/string_cleaning.py`

---

## 📊 LU16 Feature Engineering & Derived Business Columns

### Problem

Raw data columns lack business-meaningful context, making high-level decision-making difficult. We need to construct derived variables such as recency metrics, spending tiers, and composite risk scores to make data more readable and performant for downstream analysis.

### Feature Engineering Logic

- **Deployment Recency**: Calculates the days since deployment relative to a reference date.
- **Recency Tiering**: Bins recency into `Recent` (<= 15 days), `Standard` (16-30 days), or `Stale` (> 30 days) using `pd.cut`.
- **Spending Tiers**: Segments monthly cost into `Low Spend`, `Medium Spend`, or `High Spend` using `pd.qcut` (with custom fallback support).
- **Cost Risk Score**: A composite score computed as $\text{Monthly\_Cost} \times (1 + \text{Severity\_Weight})$ to assess the financial cost of operational instability.

### Run

```bash
python scripts/feature_engineering.py
```

### Output Reports

- `reports/feature_engineering_summary.csv` — Descriptive statistics of all engineered features
- `docs/lu16_feature_engineering_summary.md` — In-depth details of calculations, weightings, and Q&A
- `data/processed/final_merged_dataset_features.csv` — Processed dataset enriched with derived business features
- **Script:** `scripts/feature_engineering.py`

---

## 🌐 Future Roadmap

- 🤖 **AI Cost Advisor** — Ask natural language questions about your cloud spend
- 📝 **LLM Summaries** — Auto-generated executive reports from raw billing data
- ☁️ **Multi-Cloud Support** — AWS, GCP, and Azure in one platform
- 🔔 **Real-Time Alerts** — Anomaly notifications via Slack, Email & Teams

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**From raw data → root cause → business decisions. ☁️⚡**

*Built to make cloud cost intelligence accessible to every team.*

</div>
