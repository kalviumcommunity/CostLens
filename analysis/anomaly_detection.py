import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_folders():
    folders = ['data/raw', 'outputs', 'docs', 'analysis', 'visualizations', 'reports']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def generate_mock_data(filepath='data/raw/anomaly_data.csv'):
    np.random.seed(42)
    n = 180 # 6 months of daily data
    
    dates = pd.date_range(end=datetime.now(), periods=n, freq='D')
    
    service_cost = np.random.normal(300, 40, n)
    # Add anomalies
    service_cost[30] = 600
    service_cost[85] = 750
    service_cost[150] = 520
    
    cpu_usage = np.random.normal(60, 10, n)
    memory_usage = np.random.normal(65, 10, n)
    
    resource_utilization_score = (cpu_usage + memory_usage) / 2
    # Add utilization anomalies
    resource_utilization_score[40] = 25
    resource_utilization_score[100] = 30
    
    deployment_count = np.random.poisson(5, n)
    # Add deployment spikes
    deployment_count[10] = 18
    deployment_count[120] = 20
    
    df = pd.DataFrame({
        'date': dates,
        'service_cost': service_cost,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'deployment_count': deployment_count,
        'resource_utilization_score': resource_utilization_score
    })
    
    df.to_csv(filepath, index=False)
    logging.info(f"Mock data generated at {filepath}")
    return filepath

def load_data(filepath):
    logging.info("Loading dataset...")
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

def threshold_detection(df):
    logging.info("Running threshold anomaly detection...")
    anomalies = []
    
    # service_cost > 500
    cost_anom = df[df['service_cost'] > 500]
    for _, row in cost_anom.iterrows():
        anomalies.append({
            'timestamp': row['date'],
            'metric_name': 'service_cost',
            'value': row['service_cost'],
            'detection_method': 'Threshold (> 500)',
            'severity': 'HIGH',
            'possible_cause': 'Spike in expensive compute instances or sudden traffic surge.'
        })
        
    # resource_utilization_score < 40
    util_anom = df[df['resource_utilization_score'] < 40]
    for _, row in util_anom.iterrows():
        anomalies.append({
            'timestamp': row['date'],
            'metric_name': 'resource_utilization_score',
            'value': row['resource_utilization_score'],
            'detection_method': 'Threshold (< 40)',
            'severity': 'MEDIUM',
            'possible_cause': 'Massive over-provisioning or service outage reducing load.'
        })
        
    # deployment_count > 15
    dep_anom = df[df['deployment_count'] > 15]
    for _, row in dep_anom.iterrows():
        anomalies.append({
            'timestamp': row['date'],
            'metric_name': 'deployment_count',
            'value': row['deployment_count'],
            'detection_method': 'Threshold (> 15)',
            'severity': 'LOW',
            'possible_cause': 'Major release day or automated CI/CD loop misconfiguration.'
        })
        
    return pd.DataFrame(anomalies)

def iqr_detection(df, columns):
    logging.info("Running IQR anomaly detection...")
    anomalies = []
    
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        
        for _, row in outliers.iterrows():
            severity = 'CRITICAL' if row[col] > Q3 + 3 * IQR or row[col] < Q1 - 3 * IQR else 'HIGH'
            anomalies.append({
                'timestamp': row['date'],
                'metric_name': col,
                'value': row[col],
                'detection_method': f'IQR Bound',
                'severity': severity,
                'possible_cause': f'Statistically significant deviation beyond typical interquartile variance for {col}.'
            })
            
    return pd.DataFrame(anomalies)

def rolling_zscore_detection(df, columns, window=7, threshold=3):
    logging.info(f"Running rolling Z-Score (window={window}) anomaly detection...")
    anomalies = []
    
    for col in columns:
        rolling_mean = df[col].rolling(window=window).mean()
        rolling_std = df[col].rolling(window=window).std()
        
        z_scores = (df[col] - rolling_mean) / rolling_std
        
        # Absolute Z-Score > threshold
        outliers = df[np.abs(z_scores) > threshold]
        
        for _, row in outliers.iterrows():
            anomalies.append({
                'timestamp': row['date'],
                'metric_name': col,
                'value': row[col],
                'detection_method': f'Rolling Z-Score (>{threshold})',
                'severity': 'CRITICAL',
                'possible_cause': f'Sudden {col} spike breaking local historical trend.'
            })
            
    return pd.DataFrame(anomalies)

def create_visualizations(df, anomalies_df, output_path='visualizations/anomaly_dashboard.png'):
    logging.info("Creating anomaly visualization dashboard...")
    metrics = ['service_cost', 'resource_utilization_score', 'deployment_count']
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.plot(df['date'], df[metric], label='Value', color='steelblue', alpha=0.7)
        
        metric_anomalies = anomalies_df[anomalies_df['metric_name'] == metric]
        
        if not metric_anomalies.empty:
            ax.scatter(metric_anomalies['timestamp'], metric_anomalies['value'], 
                       color='red', label='Anomaly', zorder=5, s=50)
                       
        ax.set_title(f'{metric.replace("_", " ").title()} Trend & Anomalies')
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
    plt.xlabel('Date')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
def generate_report(anomalies_df, output_path='reports/anomaly_investigation.md'):
    logging.info("Generating anomaly investigation markdown report...")
    
    total_anomalies = len(anomalies_df)
    critical_count = len(anomalies_df[anomalies_df['severity'] == 'CRITICAL'])
    
    # Get distinct anomalies for presentation, sort by severity (Cr > H > M > L)
    severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
    anomalies_df['sev_rank'] = anomalies_df['severity'].map(severity_order)
    anomalies_sorted = anomalies_df.sort_values(['sev_rank', 'timestamp']).drop(columns=['sev_rank'])
    
    anomalies_md = anomalies_sorted[['timestamp', 'metric_name', 'value', 'severity', 'detection_method']].head(15).to_markdown(index=False)
    
    report_content = f"""# LU-25: Anomaly Detection & Risk Identification

## 1. Executive Summary
This report identifies statistical and business-logic anomalies across our cloud operations. Utilizing three discrete detection algorithms (Hard Thresholds, Interquartile Range, and Rolling Z-Scores), we have isolated events that breach acceptable operational constraints.

- **Total Anomalies Detected**: {total_anomalies}
- **Critical Anomalies**: {critical_count}

## 2. Detected Anomalies
Below is a sample of the most severe anomalies detected across the monitored metrics:

{anomalies_md}

## 3. Business Impact
Left unchecked, these anomalies represent direct risks to the organization:
- **Service Cost Spikes**: A single uncontrolled spike (e.g., $750/day vs $300 avg) rapidly depletes operational budgets and nullifies reserved instance planning.
- **Utilization Drops**: Plunging utilization scores indicate ghost infrastructure—we are paying for machines that are completely idle.
- **Deployment Surges**: Extreme outliers in daily deployment counts heavily correlate with subsequent incident spikes and SLA breaches.

## 4. Potential Causes
Based on the detected metrics, potential root causes include:
- **Cost**: Abandoned test environments or auto-scaling groups stuck at maximum bounds.
- **Utilization**: Service outages routing traffic away from active clusters, or extreme over-provisioning during peak estimation.
- **Deployments**: CI/CD automation loops retrying failed builds uncontrollably.

## 5. Recommended Actions
1. **Immediate Review**: Investigate the CRITICAL severity spikes in `service_cost` immediately via AWS Cost Explorer.
2. **Alert Integration**: Connect the rolling Z-Score algorithm to Slack/PagerDuty to alert FinOps the moment a metric breaks its 7-day trend line.
3. **Rightsizing**: Review instances flagged by the low utilization threshold and downsize them to match actual memory/CPU demand.

*(See visualizations/anomaly_dashboard.png for graphical mapping)*
"""

    with open(output_path, 'w') as f:
        f.write(report_content)

def main():
    create_folders()
    
    filepath = 'data/raw/anomaly_data.csv'
    if not os.path.exists(filepath):
        generate_mock_data(filepath)
        
    df = load_data(filepath)
    
    metrics = ['service_cost', 'resource_utilization_score', 'deployment_count']
    
    thresh_df = threshold_detection(df)
    iqr_df = iqr_detection(df, metrics)
    zscore_df = rolling_zscore_detection(df, metrics)
    
    # Combine and deduplicate anomalies
    all_anomalies = pd.concat([thresh_df, iqr_df, zscore_df], ignore_index=True)
    
    if not all_anomalies.empty:
        # Format timestamp to string for clean output/deduping
        all_anomalies['timestamp'] = all_anomalies['timestamp'].dt.strftime('%Y-%m-%d')
        # Deduplicate based on time and metric (keep highest severity if we wanted to, but dropping duplicates is fine)
        # We will sort by detection method just to keep one deterministic
        all_anomalies = all_anomalies.drop_duplicates(subset=['timestamp', 'metric_name'], keep='first')
    else:
        all_anomalies = pd.DataFrame(columns=['timestamp', 'metric_name', 'value', 'detection_method', 'severity', 'possible_cause'])
    
    # 6. Store anomalies
    out_csv = 'outputs/anomalies.csv'
    all_anomalies.to_csv(out_csv, index=False)
    logging.info(f"Anomalies stored in {out_csv}")
    
    # 7. Generate visualizations
    create_visualizations(df, all_anomalies)
    
    # 8. Generate investigation report
    generate_report(all_anomalies)
    
    print("\n" + "="*50)
    print("      ANOMALY DETECTION EXECUTION SUMMARY")
    print("="*50)
    print(f"Total Rows Evaluated: {len(df)}")
    print(f"Total Unique Anomalies Detected: {len(all_anomalies)}")
    if not all_anomalies.empty:
        print("\nSeverity Breakdown:")
        print(all_anomalies['severity'].value_counts().to_string())
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
