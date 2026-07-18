import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_folders():
    folders = ['data/raw', 'outputs', 'visualizations', 'analysis']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def generate_mock_data(filepath='data/raw/user_journey.csv'):
    """Generate mock user journey data if it doesn't exist."""
    np.random.seed(42)
    n_users = 5000
    
    # Simulating a funnel where people drop off sequentially
    dataset_uploaded = np.ones(n_users, dtype=int)
    
    # 80% pass validation
    validation_completed = np.random.binomial(1, 0.8, n_users)
    
    # Out of those who passed validation, 60% generate analysis
    analysis_generated = validation_completed * np.random.binomial(1, 0.6, n_users)
    
    # Out of those who generated analysis, 70% view the report
    report_viewed = analysis_generated * np.random.binomial(1, 0.7, n_users)
    
    # Out of those who viewed report, 40% share dashboard
    dashboard_shared = report_viewed * np.random.binomial(1, 0.4, n_users)
    
    df = pd.DataFrame({
        'user_id': [f"U{i:05d}" for i in range(1, n_users + 1)],
        'dataset_uploaded': dataset_uploaded,
        'validation_completed': validation_completed,
        'analysis_generated': analysis_generated,
        'report_viewed': report_viewed,
        'dashboard_shared': dashboard_shared
    })
    
    df.to_csv(filepath, index=False)
    logging.info(f"Mock data generated at {filepath}")
    return filepath

def load_data(filepath='data/raw/user_journey.csv'):
    """1. Load dataset using Pandas."""
    logging.info(f"Loading data from {filepath}")
    return pd.read_csv(filepath)

def build_funnel(df):
    """
    2. Build funnel stages:
    Calculates the total users at each stage.
    """
    logging.info("Building funnel stages...")
    stages = [
        'dataset_uploaded',
        'validation_completed',
        'analysis_generated',
        'report_viewed',
        'dashboard_shared'
    ]
    
    # Format stage names for better readability
    stage_names = [s.replace('_', ' ').title() for s in stages]
    
    users = [df[stage].sum() for stage in stages]
    
    funnel_df = pd.DataFrame({
        'stage': stage_names,
        'users': users
    })
    
    return funnel_df

def calculate_dropoff(funnel_df):
    """
    3. Calculate Stage Volume, Conversion Rate, Drop-Off Count, Drop-Off Percentage.
    """
    logging.info("Calculating drop-offs and conversion rates...")
    
    # Shift the users column down by 1 to get the previous stage users
    prev_users = funnel_df['users'].shift(1)
    
    # Step conversion rate (from previous stage)
    # The first stage has 100% conversion by definition (or NaN, we set to 1.0)
    step_conversion = funnel_df['users'] / prev_users
    step_conversion = step_conversion.fillna(1.0)
    
    # Drop-off count (previous stage users - current stage users)
    dropoff_count = prev_users - funnel_df['users']
    dropoff_count = dropoff_count.fillna(0).astype(int)
    
    # Drop-off percentage (from previous stage)
    dropoff_percentage = dropoff_count / prev_users
    dropoff_percentage = dropoff_percentage.fillna(0.0)
    
    # Total conversion rate (from step 1)
    initial_users = funnel_df['users'].iloc[0]
    total_conversion_rate = funnel_df['users'] / initial_users
    
    funnel_df['conversion_rate'] = step_conversion
    funnel_df['total_conversion'] = total_conversion_rate
    funnel_df['dropoff_count'] = dropoff_count
    funnel_df['dropoff_percentage'] = dropoff_percentage
    
    return funnel_df

def identify_bottleneck(funnel_df):
    """
    4. Identify Highest Drop-Off Stage, Business Impact, Potential Cause.
    """
    # Exclude the first stage since it has 0 dropoff
    dropoffs = funnel_df.iloc[1:]
    
    # Find the stage with the highest absolute drop-off count
    bottleneck_idx = dropoffs['dropoff_count'].idxmax()
    bottleneck_stage = dropoffs.loc[bottleneck_idx]
    
    bottleneck_name = bottleneck_stage['stage']
    dropoff_pct = bottleneck_stage['dropoff_percentage']
    
    # Hardcoded heuristics based on stage name for this specific pipeline
    causes = {
        'Validation Completed': 'Data formats do not match expected schemas; unclear error messages.',
        'Analysis Generated': 'High computational latency leading to user abandonment; complex parameter selection.',
        'Report Viewed': 'Users may only need the raw data output, or UI navigation to the report is hidden.',
        'Dashboard Shared': 'Lack of collaboration features; reports may not be highly exportable or executive-friendly.'
    }
    
    cause = causes.get(bottleneck_name, 'Unknown UX friction or lack of perceived value.')
    
    impact = f"Losing {dropoff_pct:.1%} of users here severely reduces the active user base and minimizes the ROI of the analytical engine."
    
    return {
        'stage': bottleneck_name,
        'dropoff_pct': dropoff_pct,
        'count': int(bottleneck_stage['dropoff_count']),
        'impact': impact,
        'cause': cause
    }

def create_visualization(funnel_df, output_path='visualizations/funnel_chart.png'):
    """
    7. Create Funnel Visualization: Horizontal Funnel Chart
    """
    logging.info("Generating horizontal funnel visualization...")
    
    stages = funnel_df['stage'].tolist()
    users = funnel_df['users'].tolist()
    
    # We will create a centered horizontal bar chart to mimic a funnel
    max_users = max(users)
    
    y_pos = np.arange(len(stages))
    
    # Calculate the left offset for each bar to center it
    left_offsets = [(max_users - u) / 2 for u in users]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create the centered bars
    bars = ax.barh(y_pos, users, left=left_offsets, color='steelblue', height=0.6, align='center')
    
    # Add text labels inside/outside bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(max_users / 2, bar.get_y() + bar.get_height()/2, 
                f'{width:,} users\n({funnel_df.iloc[i]["total_conversion"]:.1%})',
                ha='center', va='center', color='white', fontweight='bold')
    
    # Invert y-axis so the first stage is at the top
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages, fontsize=12)
    ax.invert_yaxis()
    
    # Remove x-axis and frame
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    plt.title('User Journey Funnel Analysis', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def generate_report(funnel_df, bottleneck, output_path='outputs/funnel_dropoff_report.md'):
    """
    6. Generate markdown report.
    """
    logging.info("Generating markdown report...")
    
    # Format table for markdown
    df_formatted = funnel_df.copy()
    df_formatted['conversion_rate'] = df_formatted['conversion_rate'].map(lambda x: f"{x:.1%}")
    df_formatted['dropoff_percentage'] = df_formatted['dropoff_percentage'].map(lambda x: f"{x:.1%}")
    df_formatted['total_conversion'] = df_formatted['total_conversion'].map(lambda x: f"{x:.1%}")
    
    table_md = df_formatted[['stage', 'users', 'conversion_rate', 'dropoff_count', 'dropoff_percentage']].to_markdown(index=False)
    
    report_content = f"""# LU-23: Funnel Analysis & Drop-Off Detection

## 1. Executive Summary
This report analyzes the user journey through the Cloud Cost Intelligence platform. By tracking the progression from dataset upload to dashboard sharing, we pinpointed the exact steps where users abandon the workflow. Addressing these friction points is critical for maximizing user engagement and product ROI.

## 2. Funnel Table
The table below outlines the volume of users at each stage, the conversion rate from the previous step, and the exact drop-off metrics.

{table_md}

## 3. Biggest Bottleneck
- **Highest Drop-Off Stage**: {bottleneck['stage']}
- **Users Lost**: {bottleneck['count']:,} users
- **Drop-Off Rate**: {bottleneck['dropoff_pct']:.1%} of users from the prior step failed to proceed.

## 4. Business Impact
{bottleneck['impact']} 
A severe bottleneck early in the funnel prevents users from experiencing the core value proposition of the product, directly impacting retention and potential upsells.

## 5. Potential Cause & Recommendations
**Potential Cause**: 
{bottleneck['cause']}

**Recommendations**:
1. Conduct user interviews specifically targeting users who stalled at the **{bottleneck['stage']}** stage.
2. Implement in-app telemetry (e.g., hover times, error clicks) to understand exactly where UI friction occurs.
3. Consider A/B testing a simplified, one-click version of this stage.
4. Add automated tooltips or onboarding guides directly preceding the bottleneck to assist users.

*(See visualizations/funnel_chart.png for a graphical representation)*
"""
    with open(output_path, 'w') as f:
        f.write(report_content)

def main():
    create_folders()
    
    filepath = 'data/raw/user_journey.csv'
    if not os.path.exists(filepath):
        generate_mock_data(filepath)
        
    df = load_data(filepath)
    
    funnel_df = build_funnel(df)
    funnel_df = calculate_dropoff(funnel_df)
    
    # 5. Create funnel_metrics.csv
    funnel_df[['stage', 'users', 'conversion_rate', 'dropoff_count', 'dropoff_percentage']].to_csv('outputs/funnel_metrics.csv', index=False)
    logging.info("Saved funnel metrics to outputs/funnel_metrics.csv")
    
    bottleneck = identify_bottleneck(funnel_df)
    
    create_visualization(funnel_df)
    generate_report(funnel_df, bottleneck)
    
    # 10. Print concise execution summary
    print("\n--- EXECUTION SUMMARY ---")
    print(f"Total Users Analyzed: {funnel_df['users'].iloc[0]:,}")
    print(f"Final Conversion (Dashboard Shared): {funnel_df['total_conversion'].iloc[-1]:.1%}")
    print(f"Critical Bottleneck: {bottleneck['stage']} ({bottleneck['dropoff_pct']:.1%} drop-off)")
    print("Files Generated:")
    print(" - outputs/funnel_metrics.csv")
    print(" - outputs/funnel_dropoff_report.md")
    print(" - visualizations/funnel_chart.png")
    print("-------------------------\n")

if __name__ == '__main__':
    main()
