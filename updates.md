# ☁️ CostLens AI — Outlier Detection (LU-13) Updates

This document explains the outlier detection module implemented for **Learning Unit 13 (LU-13)**, highlighting the files created, how they work, and their business impact in simple terms.

---

## 📁 Files Created & Modified

### 🆕 New Files Added
1.  **[scripts/outlier_detection.py](file:///c:/SIMWORK-project/CostLens/scripts/outlier_detection.py)**:
    *   **What it is**: The core Python script that implements statistical outlier detection.
    *   **How it works**: It automatically scans the processed datasets for numerical columns (like `Monthly_Cost` and `CPU_Usage`) and evaluates them using Z-score and Interquartile Range (IQR) methods.
2.  **[reports/outlier_cleaning_log.md](file:///c:/SIMWORK-project/CostLens/reports/outlier_cleaning_log.md)**:
    *   **What it is**: A clean, stakeholder-friendly markdown log detailing the outlier handling rules, values detected, and reasoning.
3.  **[reports/outlier_detection_summary.csv](file:///c:/SIMWORK-project/CostLens/reports/outlier_detection_summary.csv)**:
    *   **What it is**: A machine-readable spreadsheet summary containing outlier counts, total row sizes, and calculated statistical bounds.
4.  **[data/processed/cloud_cost_dataset_outliers.csv](file:///c:/SIMWORK-project/CostLens/data/processed/cloud_cost_dataset_outliers.csv)**:
    *   **What it is**: The final enriched dataset containing the cleaned data and new outlier flag columns.

---

## 📈 Explanation of the Logic (In Plain English)

An **outlier** is a data point that deviates significantly from the typical pattern (e.g., an extremely high cloud bill or an unusual CPU spike). We use two standard mathematical checks to detect them:
1.  **Z-Score ($|Z| > 3.0$)**: Checks how many standard deviations a value is away from the average. If it's more than 3, it is flagged as unusual.
2.  **IQR (1.5x Rule)**: Looks at the middle 50% of the data (between the 25th and 75th percentiles). Anything that is way above or below this normal range is flagged.

---

## 🧠 Business Handling Decisions & Impact

Not all outliers should be treated the same way. We apply different rules based on what the data represents:

### 1. `Monthly_Cost` (Financial Data)
*   **Action Taken**: **Flagged** (Adds `Monthly_Cost_outlier_flag` = `1` or `0`). We *do not* change or cap the values.
*   **Business Reason**: Billing records represent actual money spent. If we cap or delete an expensive spike, we would distort the accounting sheets. Flagging them allows the Finance/FinOps teams to see exactly when and where the spikes occurred for investigation.
*   **Impact**: Ensures 100% financial audit accuracy while highlighting runaway costs.

### 2. `CPU_Usage` / `CPU_Utilization` (Performance Data)
*   **Action Taken**: **Capped** (Winsorized to the maximum IQR boundary). We also add a trace flag `CPU_Usage_outlier_flag`.
*   **Business Reason**: CPU spikes are often temporary/transient (e.g., a service rebooting). If we leave these extreme spikes uncapped, capacity planning models might suggest we purchase more hardware than we actually need for average operations.
*   **Impact**: Stabilizes baseline infrastructure capacity planning, preventing over-provisioning and reducing wasted spend.
