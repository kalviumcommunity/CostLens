import pandas as pd
import numpy as np
import re
import os

def clean_text_column(df, column_name, mapping_dict=None):
    """
    Cleans a text column by removing whitespace, standardising case,
    removing special characters, and applying a mapping dictionary.
    """
    # 1. Whitespace Cleaning (leading/trailing)
    cleaned = df[column_name].astype(str).str.strip()
    
    # 2. Special Character Removal using Regex
    cleaned = cleaned.str.replace(r'[@#\$%&\*!]', '', regex=True)
    
    # 3. Case Normalisation (Title Case)
    cleaned = cleaned.str.title()
    
    # 4. Label Standardisation
    if mapping_dict:
        cleaned = cleaned.replace(mapping_dict)
        
    return cleaned

def main():
    # File paths
    input_file = "data/processed/cloud_cost_dataset_deduplicated.csv"
    output_file = "data/processed/cloud_cost_dataset_text_cleaned.csv"
    report_columns = "reports/string_columns_report.csv"
    report_examples = "reports/text_normalisation_examples.csv"
    report_summary = "reports/string_cleaning_summary.csv"
    
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Load dataset
    df = pd.read_csv(input_file)
    
    # STEP 1: Identify all string/object columns
    object_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    # Generate string_columns_report.csv
    report_data = []
    for col in object_cols:
        report_data.append({
            'Column Name': col,
            'Data Type': str(df[col].dtype),
            'Unique Values Count': df[col].nunique()
        })
    pd.DataFrame(report_data).to_csv(report_columns, index=False)
    
    # Define mapping dictionary
    mapping_dict = {
        "Aws": "Amazon Web Services",
        "Amazon Aws": "Amazon Web Services",
        "Amazon Web Srvices": "Amazon Web Services",
        "Gcp": "Google Cloud Platform",
        "Google Cloud": "Google Cloud Platform"
    }
    
    # To store data for before-after comparison
    examples_data = []
    summary_data = []
    
    df_cleaned = df.copy()
    
    for col in object_cols:
        original_values = df[col].copy()
        
        # Apply cleaning function
        cleaned_values = clean_text_column(df, col, mapping_dict=mapping_dict)
        df_cleaned[col] = cleaned_values
        
        # Collect examples for comparison report (only where changed)
        changed_mask = original_values.astype(str).str.strip() != cleaned_values.astype(str)
        # However, to capture all changes (including whitespace), we compare with raw strings:
        changed_mask = original_values.astype(str) != cleaned_values.astype(str)
        
        # For simplicity, let's take a sample of unique changes or all changes
        changed_df = pd.DataFrame({
            'Original Value': original_values[changed_mask],
            'Cleaned Value': cleaned_values[changed_mask]
        }).drop_duplicates()
        
        examples_data.append(changed_df)
        
        # Generate quality summary
        unique_before = original_values.nunique()
        unique_after = cleaned_values.nunique()
        replacements_made = changed_mask.sum()
        
        summary_data.append({
            'Column Name': col,
            'Unique Categories Before': unique_before,
            'Unique Categories After': unique_after,
            'Total Replacements Made': replacements_made
        })
    
    # Save before-after comparison report
    if examples_data:
        pd.concat(examples_data).to_csv(report_examples, index=False)
    else:
        pd.DataFrame(columns=['Original Value', 'Cleaned Value']).to_csv(report_examples, index=False)
        
    # Save summary report
    pd.DataFrame(summary_data).to_csv(report_summary, index=False)
    
    # Save cleaned dataset
    df_cleaned.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()
