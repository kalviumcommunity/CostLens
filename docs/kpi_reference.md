# KPI Reference & Business Metrics

This document outlines the core Key Performance Indicators (KPIs) utilized in the Cloud Cost Intelligence Platform to track financial efficiency and infrastructure reliability.

## 1. Total Cloud Spend
- **Formula**: `SUM(service_cost)` over the trailing 30 days
- **Business Meaning**: Measures the absolute financial outgoing for our cloud infrastructure for the current month. Represents our primary budget burn rate.
- **Owner**: FinOps Team
- **Update Frequency**: Daily
- **Target Range**: < $15,000 / month

## 2. Cost Growth Rate
- **Formula**: `(Current 30D Spend - Previous 30D Spend) / Previous 30D Spend`
- **Business Meaning**: Tracks the velocity of our spending. A high growth rate indicates expanding infrastructure or runaway costs, warning of future budget overruns.
- **Owner**: Director of Engineering
- **Update Frequency**: Weekly
- **Target Range**: < 5% MoM

## 3. Deployment Cost Impact
- **Formula**: `Total Spend / Total Deployments`
- **Business Meaning**: Normalizes our cloud spend against engineering velocity. If this metric rises, it means deployments are becoming heavier/more expensive over time.
- **Owner**: DevOps Team
- **Update Frequency**: Weekly
- **Target Range**: < $100 per deployment

## 4. Resource Utilization Score
- **Formula**: `AVERAGE(cpu_usage + memory_usage)`
- **Business Meaning**: Tracks whether we are actually utilizing the infrastructure we pay for. Low scores indicate over-provisioning and wasted spend.
- **Owner**: Infrastructure Team
- **Update Frequency**: Daily
- **Target Range**: > 60%

## 5. Cost Attribution Coverage
- **Formula**: `SUM(resource_tagged) / COUNT(resource_id)`
- **Business Meaning**: Measures our tagging hygiene. If resources are not tagged, finance cannot attribute the cost back to the specific team responsible.
- **Owner**: FinOps Team
- **Update Frequency**: Daily
- **Target Range**: > 90%
