import os
import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads raw CSV data from the specified filepath using Pandas.
    
    Responsibilities:
    - Validates that the input file path exists.
    - Reads the CSV file.
    - Returns the loaded Pandas DataFrame.
    """
    # Validate file existence
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: Raw data file not found at '{filepath}'")
        
    print(f"[Ingestion] Loading data from: {filepath}")
    
    # Read CSV using Pandas
    df = pd.read_csv(filepath)
    
    print(f"[Ingestion] Loaded {len(df)} records successfully.")
    return df
