# 📈 CostLens AI Metrics Dictionary

## Metric Specification Framework

---

| Field             | Detail                                           |
| ----------------- | ------------------------------------------------ |
| **Document ID**   | CLAI-MET-001                                     |
| **Version**       | 1.0.0                                            |
| **Status**        | Approved                                         |
| **Created**       | 2026-06-29                                       |
| **Last Updated**  | 2026-06-29                                       |
| **Document Type** | Metric & KPI Definition Framework                |
| **Project**       | CostLens AI                                      |
| **Tech Stack**    | SQL · Python (Pandas) · Streamlit · Power BI     |

---

## 1. Executive Summary & KPIs

The metric model for CostLens AI is structured to support three key operational roles: Engineering Leads, FinOps Analysts, and Executives (CTO/VP). Each metric is actionable, realistic to compute with SQL and Pandas, and designed for dynamic display inside our Streamlit interface.

---

## 2. Business & Financial Metrics

### 2.1 Total Spend (Daily/Weekly/Monthly)
- **Business Purpose:** Understand total platform outlays over distinct financial boundaries.
- **Formula:** 
  $$\text{Total Spend} = \sum (\text{cost\_usd})$$
- **Required Data Sources:** `fact_billing`
- **Visualization Type:** Big Number KPI + Line/Area Chart
- **Stakeholder Using It:** CTO, Finance, Engineering Managers

### 2.2 Cost per Request Unit (Unit Economics)
- **Business Purpose:** Determine if cost increases are driven by growth/demand scaling versus infrastructure inefficiency.
- **Formula:** 
  $$\text{Cost per Request Unit} = \frac{\sum (\text{cost\_usd})}{\sum (\text{requests\_count})}$$
- **Required Data Sources:** `fact_billing` joined with `fact_usage` on `date` and `service_name`.
- **Visualization Type:** Dual-Axis Time Series Line Chart (Requests vs. Cost)
- **Stakeholder Using It:** CTO, FinOps Analyst

### 2.3 Budget Utilization Percentage
- **Business Purpose:** Detect early run-away budgets before the month ends.
- **Formula:** 
  $$\text{Budget Utilization \%} = \left( \frac{\text{Actual Cumulative Spend YTD}}{\text{Allocated Monthly Budget Target}} \right) \times 100$$
- **Required Data Sources:** `fact_billing`, Static budget metadata
- **Visualization Type:** Progress Bar / Gauge Chart (Color coded: Green < 80%, Yellow 80-100%, Red > 100%)
- **Stakeholder Using It:** CTO, Engineering Lead

---

## 3. Cost Attribution & Team Metrics

### 3.1 Cost Share Percentage by Team
- **Business Purpose:** Attribute proportional cloud spending to individual business units for showback reporting.
- **Formula:** 
  $$\text{Team Cost Share \%} = \left( \frac{\sum_{\text{Team}} \text{cost\_usd}}{\sum_{\text{All}} \text{cost\_usd}} \right) \times 100$$
- **Required Data Sources:** `fact_billing` joined with `dim_teams` on `service_name`.
- **Visualization Type:** Donut Chart / Ranked Horizontal Bar Chart
- **Stakeholder Using It:** CFO, FinOps Analyst, VP of Engineering

### 3.2 Team Cost Health Score (CHS)
- **Business Purpose:** Gauge optimization behaviors and compliance across teams.
- **Formula:** 
  $$\text{CHS} = 100 - \left( 5 \times \text{Unresolved Anomalies Count} \right) - \left( 10 \times \text{Overprovisioned Services Count} \right)$$
  *(Bounded between 0 and 100)*
- **Required Data Sources:** `dim_teams`, ML Anomaly outputs, Right-sizing classification tags
- **Visualization Type:** Ranked Leaderboard Table / Heatmap Grid
- **Stakeholder Using It:** CTO, FinOps Lead

---

## 4. Infrastructure & Efficiency Metrics

### 4.1 Resource Underutilization Rate
- **Business Purpose:** Identify waste where provisioned memory and CPU are significantly under-allocated.
- **Formula:** 
  $$\text{CPU Idle Ratio} = 1 - \frac{\text{Mean(cpu\_utilization)}}{100}$$
- **Required Data Sources:** `fact_usage`
- **Visualization Type:** Scatter Plot (Cost vs. CPU Utilization)
- **Stakeholder Using It:** Systems Architect, Engineering Lead

---

## 5. Deployment Metrics

### 5.1 Deployment Cost Delta (Pre/Post release)
- **Business Purpose:** Isolate financial regressions caused by v-next application logic/releases.
- **Formula:** 
  $$\text{Cost Delta} = \text{Mean}(\text{Daily Cost}_{[t+1, t+3]}) - \text{Mean}(\text{Daily Cost}_{[t-3, t-1]})$$
  *Where $t$ represents the deployment date.*
- **Required Data Sources:** `fact_billing` joined with `fact_deployments` by `service_name`.
- **Visualization Type:** Waterfall Chart / Highlighted Event Line Markers
- **Stakeholder Using It:** Engineering Lead, Release Manager

---

## 6. Anomaly & Forecasting Metrics

### 6.1 Anomaly Deviation Ratio (ADR)
- **Business Purpose:** Measure the severity of spending spikes above normal thresholds.
- **Formula:** 
  $$\text{ADR} = \frac{\text{Actual Spend} - \text{Expected Spend}}{\text{Standard Deviation of Baseline Spend}}$$
- **Required Data Sources:** `fact_billing`, ML Model outputs
- **Visualization Type:** Time Series Line chart with anomaly markers highlighted in red.
- **Stakeholder Using It:** FinOps Analyst, Engineering Lead

### 6.2 Forecast Mean Absolute Percentage Error (MAPE)
- **Business Purpose:** Measure forecast reliability to ensure engineering can trust future budget warnings.
- **Formula:** 
  $$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^{n} \left| \frac{\text{Actual Spend}_i - \text{Forecasted Spend}_i}{\text{Actual Spend}_i} \right|$$
- **Required Data Sources:** `fact_billing`, ML Forecast table
- **Visualization Type:** Area Chart Overlay / Metric Callout Cards
- **Stakeholder Using It:** Data Scientist, FinOps Lead
