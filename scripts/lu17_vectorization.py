import pandas as pd
import numpy as np
import time

def load_data(filepath):
    """1. Load dataset using Pandas."""
    return pd.read_csv(filepath)

def calculate_loop_score(df):
    """
    2. Create a loop-based computation.
    Formula: Risk Score = (0.4 * CPU_Utilization) + (0.3 * Memory_Utilization) + (0.2 * Incident_Count * 10) + (0.1 * Deployment_Count)
    Calculate this score using a traditional Python for-loop.
    """
    risk_scores = []
    for index, row in df.iterrows():
        score = (0.4 * row['CPU_Utilization']) + \
                (0.3 * row['Memory_Utilization']) + \
                (0.2 * row['Incident_Count'] * 10) + \
                (0.1 * row['Deployment_Count'])
        risk_scores.append(score)
    
    df['Risk_Score_Loop'] = risk_scores
    return df

def calculate_numpy_score(df):
    """
    3. Create a NumPy vectorised equivalent.
    Convert required columns into NumPy arrays and perform vectorized calculation.
    """
    cpu = df['CPU_Utilization'].to_numpy()
    memory = df['Memory_Utilization'].to_numpy()
    incident = df['Incident_Count'].to_numpy()
    deployment = df['Deployment_Count'].to_numpy()
    
    risk_scores = (0.4 * cpu) + (0.3 * memory) + (0.2 * incident * 10) + (0.1 * deployment)
    
    df['Risk_Score_NumPy'] = risk_scores
    return df

def normalize_scores(df, score_column='Risk_Score_NumPy'):
    """
    5. Implement Min-Max Normalisation.
    Normalize Risk Score: (value - min) / (max - min)
    """
    scores = df[score_column].to_numpy()
    min_val = scores.min()
    max_val = scores.max()
    
    normalized = (scores - min_val) / (max_val - min_val)
    df['Normalized_Risk_Score'] = normalized
    return df

def rank_projects(df, score_column='Risk_Score_NumPy'):
    """
    6. Implement Ranking.
    Rank projects by risk score. Highest Risk = Rank 1.
    """
    # Sort and rank using numpy argsort (descending order)
    scores = df[score_column].to_numpy()
    
    # argsort sorts ascending. We want descending, so we sort negative scores
    # argsort returns indices that would sort the array
    # to get ranks, we want to know the position of each element
    # rank 1 for highest score means we need descending rank
    
    # A simple way using pandas:
    # df['Risk_Rank'] = df[score_column].rank(method='min', ascending=False).astype(int)
    
    # Using pure numpy as requested:
    # negative scores for descending order
    temp = scores.argsort()[::-1]
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(scores))
    # Rank starts at 1
    df['Risk_Rank'] = ranks + 1
    
    return df

def benchmark_execution(df):
    """
    7. Performance Benchmark.
    Measure execution time for both loop and NumPy methods.
    """
    # Benchmark Loop
    start_time = time.time()
    _ = calculate_loop_score(df.copy())
    loop_time = time.time() - start_time
    
    # Benchmark NumPy
    start_time = time.time()
    _ = calculate_numpy_score(df.copy())
    numpy_time = time.time() - start_time
    
    speedup = loop_time / numpy_time if numpy_time > 0 else float('inf')
    
    print("--- Performance Benchmark ---")
    print(f"Method\t\tExecution Time (s)\tSpeed Improvement")
    print(f"Loop\t\t{loop_time:.6f}\t\t1x")
    print(f"NumPy\t\t{numpy_time:.6f}\t\t{speedup:.2f}x")
    
    return loop_time, numpy_time, speedup

def save_outputs(df, filepath):
    """
    8. Save results.
    """
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Processed dataset saved to {filepath}")

def main():
    input_path = 'data/raw/cloud_cost_metrics.csv'
    output_path = 'data/processed/cloud_risk_scored.csv'
    
    print("1. Loading dataset...")
    df = load_data(input_path)
    
    print("2 & 3. Calculating scores to validate correctness...")
    df = calculate_loop_score(df)
    df = calculate_numpy_score(df)
    
    print("4. Validating correctness...")
    matches = np.allclose(df['Risk_Score_Loop'].to_numpy(), df['Risk_Score_NumPy'].to_numpy())
    print(f"Outputs match: {matches}")
    if not matches:
        print("Warning: Scores do not match!")
        
    print("5. Normalizing scores...")
    df = normalize_scores(df)
    
    print("6. Ranking projects...")
    df = rank_projects(df)
    
    print("7. Running performance benchmark...")
    loop_time, numpy_time, speedup = benchmark_execution(df)
    
    print("8. Saving outputs...")
    save_outputs(df, output_path)

if __name__ == "__main__":
    main()
