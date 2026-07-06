import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def identify_datetime_columns(df):
    """
    Identifies potential datetime columns (e.g. contain 'date', 'time', 'created_at', etc.)
    and generates a report.
    """
    potential_cols = []
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower() or 'at' in col.lower():
            potential_cols.append(col)
            
    # Alternatively, attempt parsing the first few rows
    datetime_cols = []
    for col in potential_cols:
        try:
            pd.to_datetime(df[col].dropna().head())
            datetime_cols.append(col)
        except Exception:
            pass
            
    return datetime_cols

def extract_time_features(df, col):
    """
    Extracts time features from a parsed datetime column.
    """
    features = pd.DataFrame()
    prefix = col.lower().split('_')[0]
    
    features[f'{prefix}_year'] = df[col].dt.year
    features[f'{prefix}_month'] = df[col].dt.month
    features[f'{prefix}_week'] = df[col].dt.isocalendar().week
    features[f'{prefix}_day_of_week'] = df[col].dt.day_name()
    features[f'{prefix}_hour'] = df[col].dt.hour
    
    return features

def main():
    input_file = "data/processed/cloud_cost_dataset_text_cleaned.csv"
    output_file = "data/processed/cloud_cost_dataset_datetime_features.csv"
    
    os.makedirs("reports", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    df = pd.read_csv(input_file)
    
    # 1. Identify datetime columns
    datetime_cols = identify_datetime_columns(df)
    
    report_data = []
    for col in datetime_cols:
        report_data.append({
            'Column Name': col,
            'Original Data Type': str(df[col].dtype),
            'Sample Value': df[col].iloc[0] if not df[col].empty else None
        })
    pd.DataFrame(report_data).to_csv("reports/datetime_columns_report.csv", index=False)
    
    # 2. Parse timestamps and extract features
    current_date = pd.Timestamp.now()
    
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 3. Extract time features
        features_df = extract_time_features(df, col)
        df = pd.concat([df, features_df], axis=1)
        
        # 4. Create Time-Since-Event feature
        prefix = col.lower().split('_')[0]
        df[f'days_since_{prefix}'] = (current_date - df[col]).dt.days
        
    # We will use Deployment_Date for the analytical questions.
    # If not present, we will fallback to the first datetime column.
    analysis_col = 'Deployment_Date' if 'Deployment_Date' in datetime_cols else datetime_cols[0]
    prefix = analysis_col.lower().split('_')[0]
    
    # 5. Day-of-Week Analysis
    day_col = f'{prefix}_day_of_week'
    if day_col in df.columns:
        day_dist = df[day_col].value_counts().reset_index()
        day_dist.columns = ['Day of Week', 'Deployments Count']
        day_dist.to_csv("reports/day_of_week_distribution.csv", index=False)
        
    # 6. Hour-of-Day Analysis
    hour_col = f'{prefix}_hour'
    if hour_col in df.columns:
        hour_dist = df[hour_col].value_counts().reset_index()
        hour_dist.columns = ['Hour of Day', 'Deployments Count']
        hour_dist.sort_values(by='Hour of Day', inplace=True)
        hour_dist.to_csv("reports/hour_of_day_distribution.csv", index=False)
        
    # 7. Time-Series Aggregation
    # Monthly Cloud Cost (requires Monthly_Cost col)
    # Weekly Deployment Count
    agg_report = []
    
    if 'Monthly_Cost' in df.columns:
        monthly_cost = df.groupby(f'{prefix}_month')['Monthly_Cost'].sum().reset_index()
        for _, row in monthly_cost.iterrows():
            agg_report.append({
                'Aggregation Type': 'Monthly Cloud Cost',
                'Time Unit': f"Month {int(row[f'{prefix}_month'])}",
                'Value': row['Monthly_Cost']
            })
            
    weekly_count = df.groupby(f'{prefix}_week').size().reset_index(name='Deployment Count')
    for _, row in weekly_count.iterrows():
        agg_report.append({
            'Aggregation Type': 'Weekly Deployment Count',
            'Time Unit': f"Week {int(row[f'{prefix}_week'])}",
            'Value': row['Deployment Count']
        })
        
    pd.DataFrame(agg_report).to_csv("reports/time_series_aggregation.csv", index=False)
    
    # 8. Generate Visualizations
    plt.figure(figsize=(10, 6))
    if 'Monthly_Cost' in df.columns:
        sns.barplot(data=monthly_cost, x=f'{prefix}_month', y='Monthly_Cost')
        plt.title('Monthly Cloud Cost Trend')
        plt.xlabel('Month')
        plt.ylabel('Total Cost')
        plt.savefig('outputs/monthly_trend_chart.png')
        plt.close()
        
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=weekly_count, x=f'{prefix}_week', y='Deployment Count', marker='o')
    plt.title('Weekly Deployment Activity')
    plt.xlabel('Week Number')
    plt.ylabel('Number of Deployments')
    plt.savefig('outputs/weekly_activity_chart.png')
    plt.close()
    
    # 9. Save Transformed Dataset
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    main()
