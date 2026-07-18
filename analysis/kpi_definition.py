import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta

# Configure clean logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_folders():
    folders = ['data/raw', 'outputs', 'docs', 'analysis']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def generate_mock_data(filepath='data/raw/kpi_data.csv'):
    """Generate mock dataset required for KPI calculations."""
    np.random.seed(42)
    n = 1000
    
    dates = pd.date_range(end=datetime.now(), periods=n, freq='D')
    
    # Simulate a cost drop recently for growth rate testing
    base_cost = np.random.normal(500, 100, n)
    base_cost[-30:] = base_cost[-30:] * 0.95  # 5% drop in recent month
    
    # Resource tagged as boolean 0 or 1
    resource_tagged = np.random.binomial(1, 0.85, n) # ~85% tagged
    
    df = pd.DataFrame({
        'resource_id': [f"RES-{i:04d}" for i in range(1, n + 1)],
        'deployment_date': dates,
        'service_cost': base_cost,
        'deployment_count': np.random.poisson(5, n),
        'cpu_usage': np.random.uniform(20, 80, n),
        'memory_usage': np.random.uniform(30, 90, n),
        'resource_tagged': resource_tagged
    })
    
    df.to_csv(filepath, index=False)
    logging.info(f"Mock data generated at {filepath}")
    return filepath

def load_data(filepath):
    logging.info("Loading dataset...")
    df = pd.read_csv(filepath)
    df['deployment_date'] = pd.to_datetime(df['deployment_date'])
    return df

# --- KPI Calculation Functions ---

def calculate_total_spend(df):
    """
    KPI: Total Cloud Spend
    Formula: SUM(service_cost) over the last 30 days
    Target: < $15,000 / month
    """
    recent_date = df['deployment_date'].max()
    start_date = recent_date - timedelta(days=30)
    recent_df = df[df['deployment_date'] > start_date]
    
    total_spend = recent_df['service_cost'].sum()
    return total_spend

def calculate_growth_rate(df):
    """
    KPI: Cost Growth Rate
    Formula: (Current 30D Spend - Previous 30D Spend) / Previous 30D Spend
    Target: < 5% growth
    """
    recent_date = df['deployment_date'].max()
    curr_start = recent_date - timedelta(days=30)
    prev_start = curr_start - timedelta(days=30)
    
    curr_spend = df[df['deployment_date'] > curr_start]['service_cost'].sum()
    prev_spend = df[(df['deployment_date'] > prev_start) & (df['deployment_date'] <= curr_start)]['service_cost'].sum()
    
    if prev_spend == 0:
        return 0.0
    
    growth_rate = (curr_spend - prev_spend) / prev_spend
    return growth_rate

def calculate_deployment_impact(df):
    """
    KPI: Deployment Cost Impact
    Formula: Total Spend / Total Deployments
    Target: < $100 per deployment
    """
    total_spend = df['service_cost'].sum()
    total_deployments = df['deployment_count'].sum()
    
    if total_deployments == 0:
        return 0.0
        
    impact = total_spend / total_deployments
    return impact

def calculate_utilization_score(df):
    """
    KPI: Resource Utilization Score
    Formula: Average of (CPU Usage % + Memory Usage %) / 2
    Target: > 60%
    """
    avg_cpu = df['cpu_usage'].mean()
    avg_mem = df['memory_usage'].mean()
    
    score = (avg_cpu + avg_mem) / 2
    return score

def calculate_attribution_coverage(df):
    """
    KPI: Cost Attribution Coverage
    Formula: (Sum of tagged resources) / (Total resources)
    Target: > 90%
    """
    total_resources = len(df)
    tagged_resources = df['resource_tagged'].sum()
    
    if total_resources == 0:
        return 0.0
        
    coverage = tagged_resources / total_resources
    return coverage

# --- Validation & Export ---

def validate_kpis(kpi_values):
    results = []
    
    # 1. Total Spend (Target: < $15,000)
    spend = kpi_values['Total Cloud Spend']
    status_spend = 'PASS' if spend < 15000 else 'FAIL'
    results.append({
        'kpi_name': 'Total Cloud Spend',
        'value': round(spend, 2),
        'target_range': '< $15000',
        'status': status_spend
    })
    
    # 2. Growth Rate (Target: < 0.05)
    growth = kpi_values['Cost Growth Rate']
    status_growth = 'PASS' if growth < 0.05 else 'FAIL'
    results.append({
        'kpi_name': 'Cost Growth Rate',
        'value': round(growth, 4),
        'target_range': '< 5%',
        'status': status_growth
    })
    
    # 3. Deployment Impact (Target: < 100)
    impact = kpi_values['Deployment Cost Impact']
    status_impact = 'PASS' if impact < 100 else 'FAIL'
    results.append({
        'kpi_name': 'Deployment Cost Impact',
        'value': round(impact, 2),
        'target_range': '< $100',
        'status': status_impact
    })
    
    # 4. Utilization Score (Target: > 60)
    score = kpi_values['Resource Utilization Score']
    status_score = 'PASS' if score > 60 else 'FAIL'
    results.append({
        'kpi_name': 'Resource Utilization Score',
        'value': round(score, 2),
        'target_range': '> 60%',
        'status': status_score
    })
    
    # 5. Attribution Coverage (Target: > 0.90)
    coverage = kpi_values['Cost Attribution Coverage']
    status_coverage = 'PASS' if coverage > 0.90 else 'FAIL'
    results.append({
        'kpi_name': 'Cost Attribution Coverage',
        'value': round(coverage, 4),
        'target_range': '> 90%',
        'status': status_coverage
    })
    
    return pd.DataFrame(results)

def generate_docs():
    logging.info("Generating KPI reference documentation...")
    doc_content = """# KPI Reference & Business Metrics

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
"""
    with open('docs/kpi_reference.md', 'w') as f:
        f.write(doc_content)
    logging.info("Documentation saved to docs/kpi_reference.md")

def main():
    create_folders()
    
    filepath = 'data/raw/kpi_data.csv'
    if not os.path.exists(filepath):
        generate_mock_data(filepath)
        
    df = load_data(filepath)
    
    logging.info("Calculating KPIs...")
    
    kpi_values = {
        'Total Cloud Spend': calculate_total_spend(df),
        'Cost Growth Rate': calculate_growth_rate(df),
        'Deployment Cost Impact': calculate_deployment_impact(df),
        'Resource Utilization Score': calculate_utilization_score(df),
        'Cost Attribution Coverage': calculate_attribution_coverage(df)
    }
    
    logging.info("Validating KPI values against targets...")
    results_df = validate_kpis(kpi_values)
    
    results_path = 'outputs/kpi_results.csv'
    results_df.to_csv(results_path, index=False)
    logging.info(f"Results saved to {results_path}")
    
    generate_docs()
    
    print("\n" + "="*40)
    print("         KPI EXECUTION SUMMARY")
    print("="*40)
    for _, row in results_df.iterrows():
        print(f"{row['kpi_name']:<30} | {row['value']:>10} | {row['status']}")
    print("="*40 + "\n")

if __name__ == '__main__':
    main()
