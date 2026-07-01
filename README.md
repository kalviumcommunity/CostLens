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

---

## ✅ LU-04 Dataset Intake & Source Validation

### Objective

Validate every incoming dataset **before** any cleaning or analysis occurs, so
bad files never enter the pipeline. The workflow inspects the raw file, confirms
it matches the expected schema, detects its encoding, and produces a structured,
auditable report.

### Validation Checks

| Stage | Check |
|---|---|
| **File** | File exists · file is non-empty · parses as valid CSV |
| **Schema** | Actual columns compared to expected schema · detects **missing** & **extra** columns |
| **Encoding** | Detects encoding (`chardet` when available) with a candidate-decode **fallback strategy** |
| **Metadata** | File name · file size · row count · column count · detected encoding · validation timestamp |

**Expected schema:** `timestamp`, `service_name`, `environment`, `cost_usd`, `deployment_id`

### Run

```bash
python scripts/dataset_intake_validation.py
```

### Report Output

A structured JSON report is written to `outputs/intake_validation_report.json`:

```json
{
  "file_name": "cloud_cost_sample.csv",
  "row_count": 20,
  "column_count": 5,
  "encoding": "utf-8",
  "missing_columns": [],
  "extra_columns": [],
  "validation_status": "PASS"
}
```

Terminal summary:

```
Dataset Intake Report
---------------------
Rows: 20
Columns: 5
Encoding: utf-8
Schema Validation: PASS
```

- **Script:** `scripts/dataset_intake_validation.py`
- **Sample dataset:** `data/raw/cloud_cost_sample.csv`
- **Report:** `outputs/intake_validation_report.json`

---

## ✅ LU-06 Dataset Profiling & Quality Assessment

### Objective

Profile `data/raw/cloud_costs.csv` and produce a structured quality assessment
**before** any cleaning or transformation, establishing a known quality baseline.

### Profiling Workflow

1. **load_dataset()** — read the raw CSV (explicit utf-8 / comma).
2. **profile_dataset()** — overview, null, duplicate and unique analysis.
3. **profile_numerical_columns()** — min, max, mean, median, std dev.
4. **profile_categorical_columns()** — unique count, top 5, frequency distribution.
5. **generate_quality_findings()** — auto-detect issues + proposed fixes.
6. **save_report()** — write JSON profile + Markdown findings.

### Quality Metrics Generated

| Category | Metrics |
|---|---|
| Overview | row count, column count, names, dtypes |
| Null analysis | per-column null count & percentage |
| Duplicate analysis | duplicate row count/%, duplicate key records |
| Unique analysis | per-column unique value count |
| Numerical | min, max, mean, median, std dev |
| Categorical | unique count, top 5, frequency distribution |

### Findings Report

`generate_quality_findings()` auto-detects: missing values, duplicate rows,
duplicate deployment records, inconsistent categories (case/whitespace) and
numeric outliers (IQR), each with a proposed fix, written to
`outputs/data_quality_findings.md`.

### Run

```bash
python scripts/dataset_profiling.py
```

### Generated Outputs

- `outputs/data_profile_report.json` — structured profiling report
- `outputs/data_quality_findings.md` — issues + proposed fixes

- **Script:** `scripts/dataset_profiling.py`

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
