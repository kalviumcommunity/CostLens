# ❓ Business Analytics Questions Specification

This document maps business queries directly to dataset joins, SQL calculations, and ML model outputs within the platform.

---

## 1. Executive Questions

### Q1: What is our total cloud spend trend across all projects this quarter?
* **Business Context:** Senior leadership needs high-level cost trajectory updates.
* **Why It Matters:** Informs high-level capital allocations and tracks overall budget health.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Month-over-month trend line highlighting absolute growth rate.

### Q2: Which product or business service represents the single highest driver of our costs?
* **Business Context:** Finding primary areas where budget is concentrated.
* **Why It Matters:** Allocates optimization focus to areas with the largest impact.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Ranked Pareto analysis highlighting service cost concentration.

### Q3: What is the quarterly cloud budget run-rate projection?
* **Business Context:** Strategic operational planning.
* **Why It Matters:** Warns executive boards of potential year-end budget overruns.
* **Required Datasets:** `fact_billing`, ML Forecast Engine
* **Expected Insight:** Projected end-of-quarter spend target compared against baseline budget.

### Q4: Are our cost levels growing faster than user requests?
* **Business Context:** Measuring gross margin performance.
* **Why It Matters:** Ensures operational scalability and infrastructure efficiency.
* **Required Datasets:** `fact_billing`, `fact_usage`
* **Expected Insight:** Trend lines comparing cost growth rate vs. transaction volume.

### Q5: What is the cloud cost share per organizational business unit?
* **Business Context:** Assigning accountability across lines of business.
* **Why It Matters:** Provides performance metrics to business unit leaders.
* **Required Datasets:** `fact_billing`, `dim_teams`
* **Expected Insight:** Donut chart splitting costs across major departments.

### Q6: How has our average cost per active customer segment changed over the last 12 months?
* **Business Context:** Tracking unit profitability.
* **Why It Matters:** Helps adjust pricing models to maintain business viability.
* **Required Datasets:** `fact_billing`, `fact_usage`
* **Expected Insight:** Unit cost trend metric grouped by customer tier.

---

## 2. Finance Questions

### Q7: What is the exact cost showback attribution for each product team?
* **Business Context:** Reconciling shared corporate billing accounts.
* **Why It Matters:** Enables accurate chargebacks and accounting.
* **Required Datasets:** `fact_billing`, `dim_teams`
* **Expected Insight:** Multi-dimensional table breaking down costs by team and cost center.

### Q8: What is the monthly budget variance across departments?
* **Business Context:** Checking budget compliance.
* **Why It Matters:** Identifies business areas that regularly blow past budgets.
* **Required Datasets:** `fact_billing`, Static budget records
* **Expected Insight:** Budget variance calculation (Actual vs. Expected).

### Q9: What are the forecasted cloud costs for next fiscal quarter?
* **Business Context:** Planning corporate budgets.
* **Why It Matters:** Prevents cash flow pinches due to unexpected infrastructure growth.
* **Required Datasets:** `fact_billing`, ML Forecast Engine
* **Expected Insight:** Point forecast with confidence intervals.

### Q10: How much of our billing is categorized as unattributed?
* **Business Context:** Improving cost tracking coverage.
* **Why It Matters:** Unattributed resources create blind spots in financial reporting.
* **Required Datasets:** `fact_billing`, `dim_teams`
* **Expected Insight:** Tracking percentage of untagged resources.

### Q11: What is the cost impact of staging/development environments versus production?
* **Business Context:** Auditing non-production overhead.
* **Why It Matters:** Dev/test environments should not exceed production ratios.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Ratio breakdown of spend across staging, development, and prod.

### Q12: Are there duplicate billing records or inconsistent currency anomalies?
* **Business Context:** Financial data cleanup.
* **Why It Matters:** Ensures reports are based on clean, reconciled numbers.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Flags showing potential duplicate billing line items.

---

## 3. Engineering Questions

### Q13: Did the latest deployment trigger a cost spike?
* **Business Context:** Post-release verification check.
* **Why It Matters:** Catches resource leaks or bad loops immediately after launch.
* **Required Datasets:** `fact_billing`, `fact_deployments`
* **Expected Insight:** Before/after cost delta analysis for the release window.

### Q14: Which specific application version is the most cost-efficient?
* **Business Context:** Comparing code optimization runs.
* **Why It Matters:** Identifies if new code optimizations are successfully lowering running costs.
* **Required Datasets:** `fact_billing`, `fact_deployments`, `fact_usage`
* **Expected Insight:** Average cost-per-request metric compared across release versions.

### Q15: Which services have the lowest average CPU and memory utilization?
* **Business Context:** Identifying idle capacity.
* **Why It Matters:** Highlights over-provisioned systems that can be scaled down.
* **Required Datasets:** `fact_usage`
* **Expected Insight:** Services sorted by lowest resource utilization.

### Q16: How does deployment frequency correlate with cost changes?
* **Business Context:** Tracking deployment cadence impact.
* **Why It Matters:** Determines if rapid release schedules introduce more cost variance.
* **Required Datasets:** `fact_deployments`, `fact_billing`
* **Expected Insight:** Cost variance plotted against release cadence.

### Q17: Which service has the largest storage growth profile?
* **Business Context:** Managing long-term data lifecycle costs.
* **Why It Matters:** Flags runaway data logs or growing DB size.
* **Required Datasets:** `fact_usage`
* **Expected Insight:** Services ranked by weekly storage growth rate.

### Q18: What is the efficiency rating of our test environments?
* **Business Context:** Controlling development environment waste.
* **Why It Matters:** Checks if dev servers are running idle over weekends.
* **Required Datasets:** `fact_usage`, `fact_billing`
* **Expected Insight:** Weekend vs. weekday usage activity maps.

---

## 4. FinOps Questions

### Q19: Which teams have the worst Cost Health Score (CHS)?
* **Business Context:** Targeting team cost accountability.
* **Why It Matters:** Highlights teams that need direct FinOps support to clean up waste.
* **Required Datasets:** `dim_teams`, Anomaly output logs
* **Expected Insight:** Leaderboard ranking team performance.

### Q20: What is the ROI of our latest right-sizing efforts?
* **Business Context:** Proving the value of optimization work.
* **Why It Matters:** Shows the actual dollar value saved by engineering cleanup efforts.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Monthly baseline vs. actual post-optimization comparison.

### Q21: What are our top 5 optimization opportunities by savings potential?
* **Business Context:** Prioritizing cleanup work.
* **Why It Matters:** Helps focus developer time on changes that save the most money.
* **Required Datasets:** `fact_usage`, `fact_billing`
* **Expected Insight:** Ranked list of target systems with potential savings calculations.

### Q22: Are we meeting our commitment discount targets?
* **Business Context:** Maximizing cloud discounts.
* **Why It Matters:** Ensures optimal utilization of purchased savings plans or reserved capacity.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Percentage of spend covered by discounted plans.

### Q23: How long does it take teams to resolve detected cost anomalies?
* **Business Context:** Tracking cost responsiveness.
* **Why It Matters:** Shorter response times minimize the blast radius of runaway spend.
* **Required Datasets:** Anomaly logs, metadata tracker
* **Expected Insight:** Average time-to-resolution metrics.

---

## 5. Operations Questions

### Q24: What is the trend of our cost per compute core?
* **Business Context:** Tracking hardware cost changes.
* **Why It Matters:** Identifies if cloud provider changes or VM type choices are getting more expensive.
* **Required Datasets:** `fact_billing`, `fact_usage`
* **Expected Insight:** Calculated monthly cost per CPU metric.

### Q25: Are there microservices with zero traffic still generating costs?
* **Business Context:** Finding abandoned systems.
* **Why It Matters:** Running idle services with no requests is direct financial waste.
* **Required Datasets:** `fact_usage`, `fact_billing`
* **Expected Insight:** List of services with 0 requests but active daily billing.

### Q26: Does our database storage utilization match the provisioned capacity?
* **Business Context:** Scaling database size correctly.
* **Why It Matters:** Highlights over-provisioned disks that can be scaled down.
* **Required Datasets:** `fact_usage`
* **Expected Insight:** Provisioned vs. consumed storage comparison.

### Q27: How much waste is caused by failed deployments?
* **Business Context:** Measuring CICD pipeline efficiency.
* **Why It Matters:** Identifies if failed builds are leaving orphaned staging resources running.
* **Required Datasets:** `fact_deployments`, `fact_billing`
* **Expected Insight:** Total cost of failed release environments.

### Q28: How does application traffic spike correlate with infrastructure auto-scaling latency?
* **Business Context:** Matching resource scaling to actual demand.
* **Why It Matters:** Balances customer performance against infrastructure cost spikes.
* **Required Datasets:** `fact_usage`
* **Expected Insight:** Scaling delay compared to traffic load.

---

## 6. Cost Optimization Questions

### Q29: Can we save money by moving specific workloads to cheaper VM families?
* **Business Context:** Hardware type optimization.
* **Why It Matters:** Modern instance types often offer better performance-to-cost ratios.
* **Required Datasets:** `fact_usage`, Instance type specs
* **Expected Insight:** Estimated savings from matching current usage to newer VM types.

### Q30: What is the estimated savings of configuring auto-shutdown schedules for staging?
* **Business Context:** Off-hours environment management.
* **Why It Matters:** Turning off dev servers during nights and weekends can cut staging costs by ~65%.
* **Required Datasets:** `fact_billing`, `fact_usage`
* **Expected Insight:** Expected savings calculations from implementing off-hours shutdown.

### Q31: Which services are candidates for database optimization based on read/write volumes?
* **Business Context:** Database sizing.
* **Why It Matters:** Avoids paying for high-tier DBs when simple storage classes would work.
* **Required Datasets:** `fact_usage`
* **Expected Insight:** List of low-activity databases.

### Q32: Are we overpaying for network egress traffic?
* **Business Context:** Data transfer optimization.
* **Why It Matters:** Unoptimized multi-region routing can lead to high data transfer fees.
* **Required Datasets:** `fact_usage`, `fact_billing`
* **Expected Insight:** Network egress cost breakdown.

---

## 7. Forecasting Questions

### Q33: What will our daily cloud spend be next week?
* **Business Context:** Short-term budget planning.
* **Why It Matters:** Helps teams catch budget issues before they affect monthly limits.
* **Required Datasets:** `fact_billing`, ML Forecast Engine
* **Expected Insight:** Day-by-day spend forecast for the upcoming 7 days.

### Q34: What is our expected spending for the next 30 days if traffic patterns remain constant?
* **Business Context:** Mid-term budget planning.
* **Why It Matters:** Helps project monthly financials with consistent business-as-usual conditions.
* **Required Datasets:** `fact_billing`, `fact_usage`, ML Forecast Engine
* **Expected Insight:** 30-day forecast projection.

### Q35: How does a projected 20% traffic increase affect our forecasted costs?
* **Business Context:** Planning for customer growth scaling.
* **Why It Matters:** Helps finance budget for increased infrastructure costs from upcoming marketing pushes.
* **Required Datasets:** `fact_billing`, `fact_usage`, ML Scenario Modeler
* **Expected Insight:** Cost growth projection modeled against traffic scaling.

### Q36: Which teams are on track to exceed their quarterly budget allocations?
* **Business Context:** Managing budget limits.
* **Why It Matters:** Allows managers to adjust priorities before budgets are breached.
* **Required Datasets:** `fact_billing`, ML Forecast Engine, Budget specs
* **Expected Insight:** List of teams with predicted budget breaches.

### Q37: What is the trend profile of our storage cost growth over the next 6 months?
* **Business Context:** Long-term storage capacity planning.
* **Why It Matters:** Prevents surprise bills from cumulative data storage growth.
* **Required Datasets:** `fact_billing`, `fact_usage`, ML Forecast Engine
* **Expected Insight:** 6-month storage spend trend forecast.

---

## 8. Risk & Anomaly Questions

### Q38: Has any service experienced an abnormal cost spike today?
* **Business Context:** Checking daily anomaly alerts.
* **Why It Matters:** Catches runaway processes or configuration errors before they run up bills.
* **Required Datasets:** `fact_billing`, ML Anomaly Engine
* **Expected Insight:** High-priority list of flagged cost anomalies.

### Q39: Which anomaly has the highest financial impact this week?
* **Business Context:** Prioritizing response work.
* **Why It Matters:** Focuses support team energy on the cost anomalies causing the most damage.
* **Required Datasets:** `fact_billing`, Anomaly outputs
* **Expected Insight:** List of active anomalies ranked by dollar deviation.

### Q40: What is the historical frequency of anomalies per service?
* **Business Context:** Checking system stability.
* **Why It Matters:** Services that repeatedly trigger anomalies likely need architecture improvements.
* **Required Datasets:** Anomaly logs
* **Expected Insight:** Anomaly count distribution grouped by service.

### Q41: How many cost anomalies were caused by failed deployments?
* **Business Context:** Feedback loop for developer operations.
* **Why It Matters:** Identifies if poor release testing is driving up platform costs.
* **Required Datasets:** `fact_deployments`, Anomaly logs
* **Expected Insight:** Anomaly count tied to failed release windows.

### Q42: Is there a seasonal cost anomaly pattern (e.g., weekend drops)?
* **Business Context:** Refining anomaly rules.
* **Why It Matters:** Reduces false alarms from normal, expected weekly traffic drops.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Day-of-week spend variation patterns.

### Q43: What is the cost impact of unpatched security anomalies (e.g., cryptojacking)?
* **Business Context:** Mitigating security costs.
* **Why It Matters:** Sudden, extreme spikes can indicate compromised servers.
* **Required Datasets:** `fact_billing`, ML Anomaly Engine
* **Expected Insight:** Extreme anomalies highlighted for immediate security review.

---

## 9. Comprehensive / Cross-Domain Questions

### Q44: What is the total estimated dollar savings from resolving all active anomalies?
* **Business Context:** Quantifying the value of active fixes.
* **Why It Matters:** Helps justify delaying feature work to resolve cost spikes.
* **Required Datasets:** `fact_billing`, Anomaly logs
* **Expected Insight:** Sum of daily excess spend across all active anomalies.

### Q45: Which services have high request volume, low cost, and high CPU usage?
* **Business Context:** Identifying efficient service design.
* **Why It Matters:** Highlights well-designed services that can serve as architecture patterns for other teams.
* **Required Datasets:** `fact_usage`, `fact_billing`
* **Expected Insight:** Cluster plot of efficiency metrics by service.

### Q46: How does the ratio of production-to-non-production cost vary by team?
* **Business Context:** Aligning environment standards.
* **Why It Matters:** Non-prod costs should generally scale proportionally with production workloads.
* **Required Datasets:** `fact_billing`, `dim_teams`
* **Expected Insight:** Production vs. non-production cost comparison per team.

### Q47: What is the average deployment cost regression duration before correction?
* **Business Context:** Checking regression fix times.
* **Why It Matters:** Tracks how quickly engineering fixes cost regressions once they're released.
* **Required Datasets:** `fact_billing`, `fact_deployments`
* **Expected Insight:** Average run-time of cost regressions.

### Q48: Which team has the highest forecasting accuracy?
* **Business Context:** Improving predictability.
* **Why It Matters:** Identifies teams with stable, predictable resource plans.
* **Required Datasets:** `fact_billing`, Forecast logs, `dim_teams`
* **Expected Insight:** Forecast MAPE accuracy ranked by team.

### Q49: What is our cost distribution across different cloud provider projects?
* **Business Context:** Provider structure overview.
* **Why It Matters:** Ensures accounts are set up correctly to prevent untracked spending.
* **Required Datasets:** `fact_billing`
* **Expected Insight:** Cost breakdown by cloud project/account.

### Q50: How has the company's overall cost per request changed year-over-year?
* **Business Context:** Tracking long-term scaling efficiency.
* **Why It Matters:** Proves if the engineering organization is successfully scaling infrastructure efficiently.
* **Required Datasets:** `fact_billing`, `fact_usage`
* **Expected Insight:** Year-over-year unit cost efficiency metric.
