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
