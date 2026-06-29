# 📅 Weekly Sprint Implementation Plan

## CostLens AI — Project Roadmap

---

| Field             | Detail                                           |
| ----------------- | ------------------------------------------------ |
| **Document ID**   | CLAI-SP-001                                      |
| **Version**       | 1.0.0                                            |
| **Status**        | Approved                                         |
| **Created**       | 2026-06-29                                       |
| **Last Updated**  | 2026-06-29                                       |
| **Document Type** | Project Schedule & Sprint Milestones             |
| **Project**       | CostLens AI                                      |
| **Sprint Cycle**  | Weekly Delivery Loops                            |

---

## Weekly Breakdown

### 🎯 Week 1: Environment Setup & Data Ingestion
- **Goals:** Establish the project foundation and construct ingestion scripts.
- **Deliverables:**
  - Standard directory structure initialized in the workspace repository.
  - Verification of Python execution environments (`requirements.txt`).
  - Data ingestion script (`src/ingestion/ingest.py`) validating basic CSV headers.
- **Concepts Covered:** Dev environment setup, Python path management, file schema checking.
- **GitHub Milestones:** `milestone-1-setup-ingestion`
- **Risks:** Missing or incorrect headers in incoming raw files.
- **Expected Outputs:** Pipeline execution output verifying raw data files load without errors.

---

### 🧹 Week 2: Data Cleaning, Normalization & SQL Storage
- **Goals:** Clean raw source files and load them into a relational database.
- **Deliverables:**
  - Python cleaning pipeline module (`src/cleaning/clean.py`) to handle missing data and remove duplicates.
  - Relational database schema layout (`sql/schema.sql`).
  - Database initialization script loading cleaned data into SQLite.
- **Concepts Covered:** Data cleaning with Pandas, SQL schema design, primary and foreign key constraints.
- **GitHub Milestones:** `milestone-2-cleaning-storage`
- **Risks:** Mismatched service names across datasets, leading to orphan records.
- **Expected Outputs:** Database loaded with clean data and checked for key referential integrity.

---

### 📊 Week 3: SQL Analytics Engine & KPI Calculations
- **Goals:** Compute business metrics and core KPIs using database queries.
- **Deliverables:**
  - SQL queries computing cost breakdowns, budget usage, and unit metrics.
  - Analytics pipeline helper (`src/analytics/queries.py`) executing database queries.
  - Power BI data export script saving query outputs to clean CSV files.
- **Concepts Covered:** Advanced SQL queries, metric calculation formulas, unit economics.
- **GitHub Milestones:** `milestone-3-analytics-engine`
- **Risks:** Inefficient SQL queries slowing down dashboard performance.
- **Expected Outputs:** Verified KPI metrics matching expected target values.

---

### 🤖 Week 4: Machine Learning Model Development
- **Goals:** Implement forecasting and anomaly detection models.
- **Deliverables:**
  - Feature engineering scripts (`src/models/features.py`) building training datasets.
  - Anomaly detection script using Isolation Forest to flag spend spikes.
  - Cost forecasting script to predict short-term and mid-term cloud spend.
- **Concepts Covered:** Scikit-Learn training pipelines, feature engineering, time-series forecasting.
- **GitHub Milestones:** `milestone-4-ml-modeling`
- **Risks:** Poor forecasting accuracy on volatile weekly spend data.
- **Expected Outputs:** Saved model files (`.pkl`) and metrics confirming model performance targets are met.

---

### 🖥️ Week 5: Dashboard Development & Deployment
- **Goals:** Build the user interface to display metrics and insights.
- **Deliverables:**
  - Streamlit dashboard (`app.py`) featuring Executive, Engineering, and FinOps tabs.
  - Integration of SQL KPIs and ML predictions into the dashboard charts.
  - Automated deployment configuration for local or cloud environments.
- **Concepts Covered:** Streamlit components, data visualization, UI design.
- **GitHub Milestones:** `milestone-5-dashboard-delivery`
- **Risks:** Slow dashboard loads due to un-cached data queries.
- **Expected Outputs:** Streamlit dashboard running locally with fast load times.

---

### 🛠️ Week 6: Automation, CI/CD & Final Project Wrap-up
- **Goals:** Configure automation pipelines and finalize project documentation.
- **Deliverables:**
  - GitHub Actions configuration file verifying tests on code pushes.
  - Test suites (`tests/`) checking data quality and logic.
  - Final project documentation, including code comments and README setup instructions.
- **Concepts Covered:** Continuous Integration, GitHub Actions, unit testing, documentation.
- **GitHub Milestones:** `milestone-6-automation-docs`
- **Risks:** GitHub Actions run failures due to environment differences.
- **Expected Outputs:** Main branch passing all automated CI checks and showing green status badges.
