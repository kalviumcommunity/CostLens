import sys
import os

# Ensure the root of the project is in the python path to prevent import issues
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import load_data
from src.processing import calculate_summary
from src.output import save_report

def main():
    """
    Main driver script orchestrating the cloud cost data workflow:
    Read (Ingestion) -> Process (Processing) -> Output (Reporting)
    """
    print("=== Starting Cloud Cost Data Pipeline ===")
    
    # Define paths
    raw_data_path = "data/raw/sample_cloud_cost_data.csv"
    report_output_path = "outputs/reports/cost_summary.txt"
    
    try:
        # Step 1: Ingestion
        df = load_data(raw_data_path)
        
        # Step 2: Processing
        summary = calculate_summary(df)
        
        # Step 3: Output
        save_report(summary, report_output_path)
        
        print("=== Pipeline Execution Completed Successfully ===")
        
    except Exception as e:
        print(f"Pipeline failed due to an error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
