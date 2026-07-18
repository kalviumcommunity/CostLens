import pandas as pd
import numpy as np
import os

def create_folders():
    folders = ['analysis', 'reports', 'outputs/groupby_results', 'visualizations', 'data/processed']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def generate_mock_data(filepath='data/processed/lu20_dataset.csv'):
    np.random.seed(42)
    n = 2000
    
    teams = ['Backend', 'Frontend', 'Data', 'DevOps', 'Mobile', 'Security']
    envs = ['dev', 'staging', 'production']
    services = ['Payments', 'Auth', 'Search', 'API', 'Database', 'Analytics', 'Notification']
    regions = ['us-east', 'us-west', 'eu-central', 'ap-south']
    months = ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06']
    
    # Generate categorical
    team_col = np.random.choice(teams, n, p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.1])
    env_col = np.random.choice(envs, n, p=[0.4, 0.3, 0.3])
    service_col = np.random.choice(services, n)
    region_col = np.random.choice(regions, n)
    month_col = np.random.choice(months, n)
    
    # Generate numerical with some bias
    # Backend costs more on average, production costs more, production has more incidents sometimes, Payments has more deployments
    base_cost = np.random.uniform(50, 500, n)
    cloud_cost = np.where(team_col == 'Backend', base_cost * 2, base_cost)
    cloud_cost = np.where(env_col == 'production', cloud_cost * 3, cloud_cost)
    
    incident_count = np.random.poisson(1, n)
    incident_count = np.where(env_col == 'production', incident_count * 2, incident_count)
    incident_count = np.where(team_col == 'Backend', incident_count + 1, incident_count)
    
    deployment_count = np.random.poisson(5, n)
    deployment_count = np.where(service_col == 'Payments', deployment_count + 3, deployment_count)
    
    df = pd.DataFrame({
        'team': team_col,
        'environment': env_col,
        'service_name': service_col,
        'region': region_col,
        'month': month_col,
        'cloud_cost': cloud_cost,
        'cpu_usage': np.random.uniform(10, 90, n),
        'memory_usage': np.random.uniform(20, 95, n),
        'deployment_count': deployment_count,
        'incident_count': incident_count,
        'active_users': np.random.randint(100, 10000, n)
    })
    
    df.to_csv(filepath, index=False)
    return filepath

def analyze_data(df):
    results = {}
    
    # 4. Group By Team
    team_summary = df.groupby('team').agg(
        Total_Cloud_Cost=('cloud_cost', 'sum'),
        Average_Cloud_Cost=('cloud_cost', 'mean'),
        Median_Cloud_Cost=('cloud_cost', 'median'),
        Incident_Count=('incident_count', 'sum'),
        Deployment_Count=('deployment_count', 'sum'),
        Record_Count=('team', 'count')
    ).reset_index()
    results['team_summary'] = team_summary
    
    # 5. Group By Environment
    env_summary = df.groupby('environment').agg(
        Total_Cloud_Cost=('cloud_cost', 'sum'),
        Average_Cloud_Cost=('cloud_cost', 'mean'),
        Average_Incidents=('incident_count', 'mean'),
        Deployment_Totals=('deployment_count', 'sum')
    ).reset_index()
    results['env_summary'] = env_summary
    
    # 6. Multi-Level GroupBy (team + environment)
    team_env_summary = df.groupby(['team', 'environment']).agg(
        Total_Cost=('cloud_cost', 'sum'),
        Total_Incidents=('incident_count', 'sum'),
        Total_Deployments=('deployment_count', 'sum'),
        Total_Active_Users=('active_users', 'sum')
    ).reset_index()
    results['team_env_summary'] = team_env_summary
    
    # 7. Rank Segments
    # Top 5 highest cost teams
    top_5_high_cost_teams = team_summary.sort_values('Total_Cloud_Cost', ascending=False).head(5)
    # Top 5 lowest cost teams
    top_5_low_cost_teams = team_summary.sort_values('Total_Cloud_Cost', ascending=True).head(5)
    
    service_summary = df.groupby('service_name').agg(
        Total_Incidents=('incident_count', 'sum'),
        Average_Cost=('cloud_cost', 'mean')
    ).reset_index()
    
    # Top incident generating services
    top_incident_services = service_summary.sort_values('Total_Incidents', ascending=False)
    
    # Best performing services (lowest incidents, reasonable cost)
    # We define "best" simply as lowest total incidents here
    best_performing_services = service_summary.sort_values('Total_Incidents', ascending=True)
    
    results['rankings'] = {
        'high_cost_teams': top_5_high_cost_teams,
        'low_cost_teams': top_5_low_cost_teams,
        'top_incident_services': top_incident_services,
        'best_performing_services': best_performing_services
    }
    
    # 8. Create Pivot Table
    pivot_table = pd.pivot_table(
        df, 
        values='cloud_cost', 
        index='team', 
        columns='environment', 
        aggfunc='sum', 
        fill_value=0
    )
    # Reset index for saving easily
    results['pivot_table'] = pivot_table.reset_index()
    
    # 9. Create Cross Tab
    crosstab_res = pd.crosstab(df['region'], df['environment'])
    results['crosstab'] = crosstab_res.reset_index()
    
    return results

def generate_insights_and_report(df, results):
    total_cost_overall = df['cloud_cost'].sum()
    total_incidents_overall = df['incident_count'].sum()
    
    # Calculate key stats
    # Highest cost team %
    top_team = results['rankings']['high_cost_teams'].iloc[0]
    top_team_name = top_team['team']
    top_team_cost = top_team['Total_Cloud_Cost']
    top_team_pct = (top_team_cost / total_cost_overall) * 100
    
    # Env incidents %
    env_inc_df = df.groupby('environment')['incident_count'].sum()
    prod_incidents = env_inc_df.get('production', 0)
    prod_inc_pct = (prod_incidents / total_incidents_overall) * 100 if total_incidents_overall > 0 else 0
    
    # Service deployments
    svc_dep_df = df.groupby('service_name')['deployment_count'].mean()
    top_dep_svc = svc_dep_df.idxmax()
    
    insights = [
        f"The {top_team_name} team contributes {top_team_pct:.1f}% of total cloud spending.",
        f"The Production environment accounts for {prod_inc_pct:.1f}% of incidents.",
        f"The {top_dep_svc} service has the highest average deployment frequency."
    ]
    
    recommendations = [
        f"Investigate {top_team_name} team resource allocation to identify optimization opportunities.",
        "Review deployment practices and QA processes in the production environment.",
        f"Optimize high-cost services associated with the {top_team_name} team."
    ]
    
    # Generate Markdown Report
    report_content = f"""# LU-20 GroupBy Aggregation & Segment Insights

## 1. Executive Summary
This report analyzes cloud operational data using categorical groupings, pivot tables, and cross-tabulations to extract actionable business segments. By breaking down costs, incidents, and deployments by Team, Environment, and Service, we expose the underlying drivers of our cloud metrics.

### Key Business Insights
- {insights[0]}
- {insights[1]}
- {insights[2]}

---

## 2. Team Analysis
The `Backend` team is historically our largest consumer of cloud resources.
The top 3 highest cost teams are:
"""
    
    for _, row in results['rankings']['high_cost_teams'].head(3).iterrows():
        report_content += f"- **{row['team']}**: ${row['Total_Cloud_Cost']:,.2f} ({int(row['Incident_Count'])} incidents)\n"
        
    report_content += "\n## 3. Environment Analysis\n"
    for _, row in results['env_summary'].iterrows():
        report_content += f"- **{row['environment'].title()}**: Total Cost = ${row['Total_Cloud_Cost']:,.2f} | Avg Incidents = {row['Average_Incidents']:.2f}\n"

    report_content += f"""
## 4. Service Analysis
- **Top Incident Generating Service**: {results['rankings']['top_incident_services'].iloc[0]['service_name']} ({results['rankings']['top_incident_services'].iloc[0]['Total_Incidents']} incidents)
- **Best Performing Service (Lowest Incidents)**: {results['rankings']['best_performing_services'].iloc[0]['service_name']} ({results['rankings']['best_performing_services'].iloc[0]['Total_Incidents']} incidents)

## 5. Top & Bottom Performers (Teams by Cost)
### Top 5 Highest Cost Teams
{results['rankings']['high_cost_teams'][['team', 'Total_Cloud_Cost']].to_markdown(index=False)}

### Top 5 Lowest Cost Teams
{results['rankings']['low_cost_teams'][['team', 'Total_Cloud_Cost']].to_markdown(index=False)}

## 6. Recommendations
1. {recommendations[0]}
2. {recommendations[1]}
3. {recommendations[2]}
"""
    
    with open('reports/groupby_insights.md', 'w') as f:
        f.write(report_content)

def save_outputs(results):
    out_dir = 'outputs/groupby_results/'
    results['team_summary'].to_csv(os.path.join(out_dir, 'team_summary.csv'), index=False)
    results['env_summary'].to_csv(os.path.join(out_dir, 'environment_summary.csv'), index=False)
    results['team_env_summary'].to_csv(os.path.join(out_dir, 'team_environment_summary.csv'), index=False)
    results['pivot_table'].to_csv(os.path.join(out_dir, 'pivot_table.csv'), index=False)
    results['crosstab'].to_csv(os.path.join(out_dir, 'crosstab.csv'), index=False)

def main():
    create_folders()
    
    print("Generating and loading data...")
    filepath = generate_mock_data()
    df = pd.read_csv(filepath)
    
    print("Performing groupby aggregations...")
    results = analyze_data(df)
    
    print("Saving outputs...")
    save_outputs(results)
    
    print("Generating insights and report...")
    generate_insights_and_report(df, results)
    
    print("LU-20 Analysis Complete.")

if __name__ == '__main__':
    main()
