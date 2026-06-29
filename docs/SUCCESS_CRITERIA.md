# 🏆 Success Criteria & Validation Framework

This document outlines the validation standards required to confirm the platform meets technical, functional, and product delivery requirements.

---

## 1. Functional Success Criteria

### FC-1: End-to-End Pipeline Execution
* **Description:** The system must run the ingestion, cleaning, and storage pipeline in a single step.
* **Validation Method:** Execute the pipeline script (`python src/ingestion/run_pipeline.py`) from a clean environment.
* **Pass Condition:** The pipeline finishes with an exit code of `0` and populates the SQLite/PostgreSQL database tables.

### FC-2: Cost Attribution Matching
* **Description:** Every dollar in the raw billing data must be attributed to an owning team.
* **Validation Method:** Query the database to find records where the team field is blank or null.
* **Pass Condition:** Exactly `0` billing records are left unattributed after running the pipeline.

---

## 2. Technical Success Criteria

### TC-1: Automated Testing Suite
* **Description:** The platform codebase must be covered by unit tests.
* **Validation Method:** Execute tests with coverage tracking (`pytest --cov=src`).
* **Pass Condition:** Core pipeline and utility files reach at least `80%` test coverage.

### TC-2: Continuous Integration Build Checks
* **Description:** Code pushes to main branches must pass style and functional tests automatically.
* **Validation Method:** Check run results in the GitHub Actions dashboard.
* **Pass Condition:** Linting (`flake8`) and unit tests pass with green checks on every push.

---

## 3. Analytics Success Criteria

### AC-1: Metric Calculation Precision
* **Description:** Business KPIs computed in SQL must match expected values.
* **Validation Method:** Compare SQL calculations against manually calculated Pandas checks.
* **Pass Condition:** Calculated metrics match manual checks with `100%` accuracy.

### AC-2: Unit Economics Correlation
* **Description:** The platform must accurately compute traffic-based unit costs (Cost per Request).
* **Validation Method:** Run unit cost queries on days with high traffic spikes.
* **Pass Condition:** The output matches expected usage patterns without calculation errors.

---

## 4. Machine Learning Success Criteria

### MC-1: Anomaly Detection Performance
* **Description:** The Isolation Forest model must identify unexpected spending spikes.
* **Validation Method:** Run model evaluation on a test set containing labeled spend anomalies.
* **Pass Condition:** The anomaly detection model achieves at least `85%` precision.

### MC-2: Forecasting Accuracy
* **Description:** The time-series forecasting model must project future spending trends.
* **Validation Method:** Compare the model's 7-day forecast predictions against actual cost results.
* **Pass Condition:** The forecast model achieves a Mean Absolute Percentage Error (MAPE) of `10%` or less.

---

## 5. Dashboard Success Criteria

### DC-1: Page Load Performance
* **Description:** The dashboard must load charts and data views quickly.
* **Validation Method:** Measure page render times using browser development tools.
* **Pass Condition:** All pages load and display charts in under `3 seconds`.

### DC-2: Active Filter Verification
* **Description:** Dropdown filters for dates and teams must update all charts on the page.
* **Validation Method:** Change filter selections in the sidebar and verify chart updates.
* **Pass Condition:** Filter changes trigger updates on all dependent visualizations without errors.

---

## 6. Documentation Success Criteria

### DOC-1: Technical Setup Guide
* **Description:** Setup instructions must allow developers to run the project from scratch.
* **Validation Method:** Clone the repository to a clean machine and follow the instructions in the README.
* **Pass Condition:** The local setup is completed and the app runs without troubleshooting steps.
