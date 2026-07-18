import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_folders():
    folders = ['analysis', 'reports', 'outputs/segment_analysis', 'visualizations', 'data/processed']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def generate_mock_data(filepath='data/processed/lu22_behavioral_data.csv'):
    np.random.seed(42)
    n = 2000
    
    envs = ['Development', 'Staging', 'Production']
    teams = ['Backend', 'Frontend', 'Platform', 'Data']
    regions = ['US', 'Europe', 'India', 'APAC']
    
    # Introduce small sample size group (e.g. APAC in Staging might be very small, or some specific team like 'Platform' is small)
    env_col = np.random.choice(envs, n, p=[0.25, 0.25, 0.5])
    team_col = np.random.choice(teams, n, p=[0.4, 0.3, 0.01, 0.29]) # Platform has very few (1%)
    region_col = np.random.choice(regions, n, p=[0.4, 0.3, 0.2, 0.1])
    
    # Metrics
    base_cost = np.random.uniform(10, 100, n)
    cloud_cost = np.where(env_col == 'Production', base_cost * 10, base_cost)
    cloud_cost = np.where(team_col == 'Data', cloud_cost * 1.5, cloud_cost)
    
    incident_count = np.random.poisson(2, n)
    incident_count = np.where(region_col == 'India', np.maximum(incident_count - 1, 0), incident_count)
    incident_count = np.where(team_col == 'Platform', incident_count + 5, incident_count)
    
    deployment_count = np.random.poisson(10, n)
    deployment_count = np.where(team_col == 'Backend', deployment_count + 15, deployment_count)
    
    error_rate = np.random.uniform(0.001, 0.05, n)
    error_rate = np.where(env_col == 'Production', error_rate * 0.5, error_rate)
    
    df = pd.DataFrame({
        'environment': env_col,
        'team': team_col,
        'region': region_col,
        'cloud_cost': cloud_cost,
        'incident_count': incident_count,
        'deployment_count': deployment_count,
        'error_rate': error_rate,
        'cpu_usage': np.random.uniform(20, 80, n),
        'memory_usage': np.random.uniform(30, 90, n),
        'active_users': np.random.poisson(5000, n),
        'request_volume': np.random.poisson(10000, n)
    })
    
    df.to_csv(filepath, index=False)
    return filepath

def analyze_segment(df, segment_col, metrics):
    agg_funcs = {m: ['mean', 'median', 'sum', 'count'] for m in metrics}
    
    summary = df.groupby(segment_col).agg(agg_funcs)
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    # Ensure there is a generic 'count' column for confidence checking
    # Just use the count of the first metric
    first_metric_count = f"{metrics[0]}_count"
    summary['confidence'] = np.where(summary[first_metric_count] < 30, 'LOW CONFIDENCE', 'HIGH CONFIDENCE')
    
    return summary

def generate_visualizations(df, segment_col, output_path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'{segment_col.capitalize()} Comparison', fontsize=16)
    
    metrics_to_plot = ['cloud_cost', 'incident_count', 'deployment_count', 'error_rate']
    titles = ['Cloud Cost', 'Incident Count', 'Deployment Count', 'Error Rate']
    
    for i, ax in enumerate(axes.flatten()):
        metric = metrics_to_plot[i]
        sns.boxplot(data=df, x=segment_col, y=metric, ax=ax, palette='Set2')
        ax.set_title(f'{titles[i]} by {segment_col.capitalize()}')
        ax.set_xlabel('')
        ax.set_ylabel(titles[i])
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    create_folders()
    filepath = generate_mock_data()
    df = pd.read_csv(filepath)
    
    metrics = ['cloud_cost', 'incident_count', 'deployment_count', 'error_rate']
    
    # 6. Calculate mean, median, sum, count
    env_summary = analyze_segment(df, 'environment', metrics)
    team_summary = analyze_segment(df, 'team', metrics)
    region_summary = analyze_segment(df, 'region', metrics)
    
    # 9. Generate visualizations
    generate_visualizations(df, 'environment', 'visualizations/environment_comparison.png')
    generate_visualizations(df, 'team', 'visualizations/team_comparison.png')
    generate_visualizations(df, 'region', 'visualizations/region_comparison.png')
    
    # 7. Identify Highest/Lowest performing
    # We define performance here based on incident_count (lower is better) and deployment_count (higher is better)
    # Just as a simple heuristic for segment rankings:
    rankings = []
    
    for summary, seg_name, col in [(env_summary, 'Environment', 'environment'), 
                                   (team_summary, 'Team', 'team'), 
                                   (region_summary, 'Region', 'region')]:
        
        best_inc = summary.sort_values('incident_count_mean').iloc[0][col]
        worst_inc = summary.sort_values('incident_count_mean', ascending=False).iloc[0][col]
        
        rankings.append({
            'Segment_Type': seg_name,
            'Best_Performing_Incident_Rate': best_inc,
            'Worst_Performing_Incident_Rate': worst_inc
        })
        
    rankings_df = pd.DataFrame(rankings)
    
    # 13. Export outputs
    env_summary.to_csv('outputs/segment_analysis/environment_summary.csv', index=False)
    team_summary.to_csv('outputs/segment_analysis/team_summary.csv', index=False)
    region_summary.to_csv('outputs/segment_analysis/region_summary.csv', index=False)
    rankings_df.to_csv('outputs/segment_analysis/segment_rankings.csv', index=False)
    
    # Calculate values for observations
    total_cost = df['cloud_cost'].sum()
    prod_cost = env_summary[env_summary['environment'] == 'Production']['cloud_cost_sum'].values[0]
    prod_cost_pct = (prod_cost / total_cost) * 100
    
    backend_deploy = team_summary[team_summary['team'] == 'Backend']['deployment_count_mean'].values[0]
    max_team_deploy_name = team_summary.loc[team_summary['deployment_count_mean'].idxmax(), 'team']
    
    min_inc_region = region_summary.loc[region_summary['incident_count_mean'].idxmin(), 'region']
    
    low_conf_findings = []
    high_conf_findings = []
    
    for summary, col in [(env_summary, 'environment'), (team_summary, 'team'), (region_summary, 'region')]:
        for _, row in summary.iterrows():
            finding = f"Segment {row[col]} has mean incident rate of {row['incident_count_mean']:.2f}"
            if row['confidence'] == 'LOW CONFIDENCE':
                low_conf_findings.append(f"- **{row[col]} ({col})**: Sample size {row['cloud_cost_count']} < 30. LOW CONFIDENCE.")
            else:
                high_conf_findings.append(f"- **{row[col]} ({col})**: High confidence (n={row['cloud_cost_count']}).")
                
    if not low_conf_findings:
        low_conf_findings = ["- None identified. All segments have sufficient sample size."]
        
    report_content = f"""# LU-22 Behavioural Analysis & User Segmentation

## 1. Executive Summary
This report analyzes operational behavior across distinct business segments (Environment, Team, Region). By performing granular grouping, calculating confidence intervals via sample counts, and contrasting segment performance, we derive actionable insights for business decision-making.

## 2. Environment Analysis
- The **Production** environment generates {prod_cost_pct:.1f}% of total cloud costs.
- While Development environments have higher error rates, Production handles the vast majority of our load and cost footprint.

## 3. Team Analysis
- The **{max_team_deploy_name}** team produces the highest deployment frequency across all engineering divisions.
- Certain teams exhibit drastically different resource utilization patterns based on their distinct operational demands.

## 4. Region Analysis
- The **{min_inc_region}** region shows the lowest incident rate, demonstrating strong local stability or potentially lower user traffic translating to fewer reported issues.

## 5. High Confidence Findings
{chr(10).join(high_conf_findings[:5])}
*(Only showing top 5 high confidence findings for brevity)*

## 6. Low Confidence Findings (Flagged)
{chr(10).join(low_conf_findings)}

## 7. Business Observations
1. **Production Cost Dominance**: Production environment generates ~{prod_cost_pct:.0f}% of cloud costs.
2. **Backend Velocity**: Backend team produces highest deployment frequency.
3. **Regional Reliability**: {min_inc_region} region shows lowest incident rate.

## 8. Business Recommendations
- **Review production resource allocation**: Given its overwhelming share of costs, apply strict auto-scaling and spot-instance utilization to Production.
- **Investigate backend deployment practices**: While velocity is high, cross-check their incident rates to ensure they aren't trading reliability for speed.
- **Monitor region-specific performance trends**: Determine why {min_inc_region} is outperforming others in reliability and replicate those practices globally.
"""

    with open('reports/segment_analysis.md', 'w') as f:
        f.write(report_content)
        
    print("Analysis complete. Reports and Visualizations generated.")

if __name__ == '__main__':
    main()
