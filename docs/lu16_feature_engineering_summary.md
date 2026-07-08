# LU-16 :: Feature Engineering & Derived Business Columns Summary

This document details the feature engineering methodologies, business logic, weighting choices, and validation rules implemented for the CostLens platform. It also answers the core conceptual questions for Learning Unit 16.

---

## 🧠 Core Concepts & Analytical Rationale

### 1. What is Feature Engineering & Why Derived Features Outperform Raw Columns
*   **Definition**: Feature engineering is the process of using domain knowledge to extract new variables (features) from raw data.
*   **Why they outperform raw columns**: 
    *   **Contextual Value**: Raw numerical columns (like `Monthly_Cost` or `Severity` string labels) lack business context on their own. For example, a $1,000 monthly cost is acceptable for a business-critical system, but high-risk for an unstable, non-critical one.
    *   **Model Performance**: Machine learning algorithms (and human analysts) model linear or non-linear relationships much more easily when complex interactions are pre-computed (e.g. ratios, composite risk scores) rather than expecting the model to infer them from raw inputs.
    *   **Signal Amplification**: Tiering/binning removes noise from raw continuous values (like minor day-to-day cost fluctuations) and amplifies signals (such as "High Spend" vs. "Low Spend" bands).

### 2. Difference Between `pd.cut` and `pd.qcut` & When to Use Which
*   **`pd.cut` (Value-Based Binning)**:
    *   **How it works**: Divides the range of values into intervals of equal width, or custom defined boundaries.
    *   **When to use**: Best when there are specific, predefined business thresholds. For example, in `Deployment_Recency_Days`, we want to classify anything older than 30 days as `Stale` based on operational SLA, regardless of the distribution of our deployments.
*   **`pd.qcut` (Frequency-Based Binning)**:
    *   **How it works**: Divides the data into quantiles (e.g., tertiles, quartiles) such that each bin contains roughly the same number of data points.
    *   **When to use**: Best when you want to look at relative distributions (e.g. segmenting projects into low, medium, and high spend groups where each group occupies 33.3% of the total projects). This adapts naturally as overall cloud spend grows.

### 3. Composite Score Construction & Weighting Decisions
We constructed the **`Cost_Risk_Index`** to combine financial cost and operational risk into a single metric:
$$\text{Cost\_Risk\_Index} = \text{Monthly\_Cost} \times (1.0 + \text{Severity\_Weight})$$

*   **Severity Weights**:
    *   `Critical` = 5.0 (system-down issues that require immediate mitigation).
    *   `High` = 3.0 (significant degradation).
    *   `Medium` = 2.0 (minor issue with workarounds).
    *   `Low` = 1.0 (trivial issues).
    *   `None` / `NaN` = 0.0 (no incidents, baseline risk).
*   **Rationale**: Adding `1.0` to the weight acts as a multiplier. If a project has no incidents (`Severity_Weight` = 0.0), its index is exactly its cost. If it suffers a `High` severity incident, its cost is multiplied by `4.0` ($1 + 3$), reflecting that an expensive service suffering major degradation is a severe operational liability.

### 4. Downstream Usage of the Most Business-Meaningful Feature
*   **Feature**: **`Cost_per_Risk_Unit`** (Ratio Metric)
    *   **Formula**: $\text{Monthly\_Cost} / (1.0 + \text{Severity\_Weight})$
    *   **Downstream Usage**: This represents the financial return on operational stability. 
        *   If a resource is expensive but highly stable (no incidents), the `Cost_per_Risk_Unit` is high (near baseline cost). 
        *   If a resource is cheap but highly unstable, the value is low.
        *   FinOps teams use this downstream in optimization dashboards to identify "low-value/high-risk" resources—assets where we spend substantial money but receive poor operational reliability (low Cost per Risk Unit), marking them as immediate candidates for architectural refactoring.

### 5. Preventing Data Leakage in Feature Engineering Validation
**Data Leakage** occurs when information from outside the training dataset (such as target labels or future data) is inadvertently used to create features, leading to overly optimistic evaluation metrics.

To validate that our features do not introduce data leakage:
1.  **Strict Temporal Split**: Ensure that all date-based calculations (like `Deployment_Recency_Days`) are computed relative to an **analysis cutoff date** (reference date) representing the present moment, rather than leaking future dates or timestamps into the calculation.
2.  **No Group-Level Statistics on Test Sets**: Avoid using global dataset parameters (like global mean, standard deviation, or global quantile cuts) inside feature engineering functions during training. Instead, calculate parameters (like bin boundaries in `pd.qcut` or mean values) solely on the **training fold** and apply those fixed boundaries/parameters to the test set during inference.
3.  **Target Exclusivity**: Never use target variables (e.g. future cloud cost predictions or actual incident durations) to construct features like `Cost_Risk_Index`. Features must be derived entirely from attributes known at the time of the event.
