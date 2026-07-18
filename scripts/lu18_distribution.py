import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(filepath):
    """1. Load the processed dataset."""
    df = pd.read_csv(filepath)
    # Rename for standard usage if necessary, based on previous step
    if 'Risk_Score_NumPy' in df.columns:
        df['Risk_Score'] = df['Risk_Score_NumPy']
    return df

def plot_distribution(df, column, output_dir):
    """
    3. Generate Distribution Visualizations.
    Create Histogram and KDE Plot, save to output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    # sns.histplot automatically generates both if kde=True
    sns.histplot(df[column], kde=True, bins=50, color='royalblue', edgecolor='black')
    
    plt.title(f'Distribution of {column}', fontsize=16)
    plt.xlabel(column, fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(axis='y', alpha=0.75)
    
    output_path = os.path.join(output_dir, f"{column.lower()}_distribution.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved distribution plot for {column} at {output_path}")

def calculate_statistics(df, columns):
    """
    4. Compute Statistical Metrics.
    Calculate Mean, Median, Std Dev, Skewness, Kurtosis.
    """
    stats = []
    for col in columns:
        stats.append({
            'Column': col,
            'Mean': df[col].mean(),
            'Median': df[col].median(),
            'Standard_Deviation': df[col].std(),
            'Skewness': df[col].skew(),
            'Kurtosis': df[col].kurtosis()
        })
    return pd.DataFrame(stats)

def save_reports(stats_df, output_path):
    """Save statistics to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stats_df.to_csv(output_path, index=False)
    print(f"Saved distribution statistics to {output_path}")

def segment_projects(df, output_dir):
    """
    8. Segment Comparison Analysis.
    Create project categories: Low Cost, Medium Cost, High Cost.
    Compare distributions of Incident_Count and Risk_Score.
    """
    # Define segments based on quantiles (33.3%, 66.6%)
    q1 = df['Monthly_Cost'].quantile(0.3333)
    q2 = df['Monthly_Cost'].quantile(0.6667)
    
    def categorize(cost):
        if cost <= q1: return 'Low Cost'
        elif cost <= q2: return 'Medium Cost'
        else: return 'High Cost'
        
    df['Cost_Segment'] = df['Monthly_Cost'].apply(categorize)
    df['Cost_Segment'] = pd.Categorical(df['Cost_Segment'], categories=['Low Cost', 'Medium Cost', 'High Cost'], ordered=True)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot Incident_Count by Segment
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Cost_Segment', y='Incident_Count', data=df, palette='Set2')
    plt.title('Incident Count by Cost Segment', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'incident_count_by_segment.png'))
    plt.close()
    
    # Plot Risk_Score by Segment
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Cost_Segment', y='Risk_Score', data=df, palette='Set2')
    plt.title('Risk Score by Cost Segment', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'risk_score_by_segment.png'))
    plt.close()

def generate_business_insights():
    """
    Generate markdown report text (usually this might write to a file, 
    but for this task we can print it and let the main flow write to docs).
    """
    pass

def main():
    input_file = 'data/processed/cloud_risk_scored.csv'
    dist_out_dir = 'outputs/distributions'
    stats_out_file = 'reports/distribution_statistics.csv'
    
    print("Loading dataset...")
    df = load_data(input_file)
    
    cols_to_analyze = ['Monthly_Cost', 'Incident_Count', 'Risk_Score']
    
    print("Generating distribution visualizations...")
    for col in cols_to_analyze:
        plot_distribution(df, col, dist_out_dir)
        
    print("Calculating statistics...")
    stats_df = calculate_statistics(df, cols_to_analyze)
    save_reports(stats_df, stats_out_file)
    
    print("Segmenting projects and comparing...")
    segment_projects(df, dist_out_dir)
    print("Analysis complete.")

if __name__ == '__main__':
    main()
