import pandas as pd
import numpy as np

def generate_data(filepath, num_rows=100000):
    np.random.seed(42)
    data = {
        'Project_ID': [f'PRJ-{i:06d}' for i in range(1, num_rows + 1)],
        'Monthly_Cost': np.random.uniform(100, 10000, num_rows),
        'CPU_Utilization': np.random.uniform(0, 100, num_rows),
        'Memory_Utilization': np.random.uniform(0, 100, num_rows),
        'Incident_Count': np.random.randint(0, 10, num_rows),
        'Deployment_Count': np.random.randint(1, 50, num_rows)
    }
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(f"Data generated at {filepath}")

if __name__ == "__main__":
    import os
    os.makedirs('data/raw', exist_ok=True)
    generate_data('data/raw/cloud_cost_metrics.csv')
