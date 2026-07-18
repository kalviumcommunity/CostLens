# LU-18: Distribution Analysis for Business Trends

## 1. Distribution Findings

We analyzed the distributions of three key cloud infrastructure metrics:
- **Monthly Cost**: Represents the total monthly expenditure per project.
- **Incident Count**: Represents the frequency of operational incidents per project.
- **Risk Score**: A weighted composite metric highlighting infrastructure operational risk.

Visualizations including Histograms and Kernel Density Estimation (KDE) plots have been generated and saved to `outputs/distributions/`.

## 2. Skewness Interpretation

Skewness measures the asymmetry of a distribution around its mean.

* **Monthly Cost (Skewness: ~0.00)**: **Symmetric**. The costs are evenly distributed around the mean. In a real-world scenario, costs are typically heavily right-skewed (positively skewed), meaning a few projects consume the majority of the budget. Here, the uniform distribution implies that cloud spend is distributed equally across all tiers of projects.
* **Incident Count (Skewness: ~0.00)**: **Symmetric**. Incidents occur at a flat, predictable rate across the portfolio. 
* **Risk Score (Skewness: ~0.00)**: **Symmetric**. Operational risk is evenly distributed.

*Business Meaning*: A symmetric distribution in cloud costs and incidents suggests a highly decentralized environment where no single team or project is disproportionately impacting the infrastructure or the budget. Optimization efforts must be broad-based rather than targeted at a few "heavy hitters."

## 3. Kurtosis Interpretation

Kurtosis measures the "tailedness" of a distribution (i.e., the presence of outliers).

* **Monthly Cost (Kurtosis: ~ -1.20)**: **Low Kurtosis (Platykurtic)**.
* **Incident Count (Kurtosis: ~ -1.22)**: **Low Kurtosis (Platykurtic)**.
* **Risk Score (Kurtosis: ~ -0.49)**: **Low Kurtosis (Platykurtic)**.

*Business Implications*: Low kurtosis indicates a lack of extreme outliers. There are no "runaway" projects causing massive, unexpected billing spikes, nor are there localized clusters of catastrophic incident counts. The environment is highly stable and bounded, though it lacks the typical "Pareto Principle" (80/20 rule) optimization opportunities.

## 4. Segment Analysis

Projects were segmented into three tiers based on Monthly Cost percentiles:
1. **Low Cost** (Bottom 33%)
2. **Medium Cost** (Middle 33%)
3. **High Cost** (Top 33%)

Side-by-side boxplots were generated to compare these segments:
* **Incident Count by Cost Segment**: Incidents remain relatively consistent across all cost tiers, showing no correlation between how much a project costs and how unstable it is.
* **Risk Score by Cost Segment**: Risk scores remain completely independent of the cost segment.

## 5. Identified Business Patterns (Hidden Insights)

**Hidden Pattern Identified: The "Flat-Tier" Operational Model**
Contrary to typical cloud environments where 20% of projects generate 80% of costs and incidents (high kurtosis, right-skewed), this dataset reveals a **Flat-Tier Operational Model**. 
* **Insight**: Risk and incident frequency are entirely decoupled from project cost. High-cost projects are just as likely to experience operational incidents as low-cost projects. 
* **Implication**: This indicates an absence of "premium" operational support for high-investment projects. We are not achieving economies of scale regarding reliability.

## 6. Business Recommendations
1. **Broad-based Cost Optimization**: Since spend is not concentrated in a few outliers, cost-saving initiatives (like committed use discounts or global rightsizing policies) must be applied across the entire organization simultaneously to see meaningful ROI.
2. **Tiered Reliability Engineering**: High-cost projects should theoretically have lower incident rates due to better architecture or dedicated support. We recommend implementing strict Service Level Objectives (SLOs) focused specifically on the "High Cost" segment to reduce their incident counts and justify their higher spend.
