# Datetime Feature Engineering Strategy

## Overview
This document outlines the pipeline for transforming raw timestamp strings into actionable time-series features. Transforming dates into categorical and numerical time features enables powerful analytical aggregations such as trend analysis, seasonality detection, and time-based filtering.

## 1. Timestamp Columns Identified
During the data loading phase, columns containing date and time information were identified and converted to proper `datetime64` objects. Typical columns include:
- `Deployment_Date`: When a cloud resource was provisioned.
- `Billing_Date`: The day associated with a particular cloud cost record.

## 2. Features Extracted
To enable time-series slicing and dicing, the following features are extracted from the base timestamps:
- **Year**: Extracted using `.dt.year` for high-level annual reporting.
- **Month**: Extracted using `.dt.month` to aggregate costs and deployments on a monthly cadence.
- **Week Number**: Extracted using `.dt.isocalendar().week` for tracking weekly operational velocity.
- **Day of Week**: Extracted using `.dt.day_name()` (e.g., Monday, Tuesday) to understand deployment cycles and team habits.
- **Hour of Day**: Extracted using `.dt.hour` to identify peak provisioning periods (when applicable).

### Business Meaning
- **Month/Week**: Allows the finance team to monitor monthly burn rates against the budget.
- **Day of Week / Hour**: Enables the engineering team to map deployments to potential cost spikes and system loads.

## 3. Time-Since-Event Explanation
Time-Since-Event features measure the duration between a past event and the current analysis date.
- **Feature**: `days_since_deployment` / `days_since_billing`
- **Calculation**: `Current Date - Event Date`
- **Business Use Case**: Helps identify stale resources (e.g., deployments that have been active for >90 days without updates) that might be candidates for decommissioning or right-sizing.

## 4. Aggregation Results
With extracted features, time-series aggregations become trivial. The generated reports include:
- **Monthly Cloud Cost**: Total spend aggregated by `Month`.
- **Weekly Deployment Count**: Total number of provisioned resources aggregated by `Week Number`.
- **Day of Week Distribution**: Volume of deployments by day (e.g., assessing if deployments happen safely during mid-week or riskily on Fridays).
- **Hour of Day Distribution**: Assessing whether automated scaling happens continuously or in bursts.

These aggregations are visualised and saved as charts in the `outputs/` directory to facilitate rapid insights for stakeholders.
