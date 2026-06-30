import pandas as pd
from typing import Dict, Any

def calculate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Processes the raw cloud cost DataFrame to calculate summary metrics.
    
    Responsibilities:
    - Calculates the total cloud cost.
    - Calculates the average cloud cost per record.
    - Calculates the total cost broken down by environment.
    - Returns a dictionary containing the processed summary statistics.
    """
    print("[Processing] Running analytical summary calculations...")
    
    # Ensure cost column is numeric
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0)
    
    # Calculate total cost
    total_cost = float(df['cost'].sum())
    
    # Calculate average cost
    average_cost = float(df['cost'].mean()) if len(df) > 0 else 0.0
    
    # Calculate cost by environment
    cost_by_env = df.groupby('environment')['cost'].sum().to_dict()
    
    summary = {
        'total_cost': total_cost,
        'average_cost': average_cost,
        'cost_by_environment': cost_by_env
    }
    
    print("[Processing] Summary processing complete.")
    return summary
