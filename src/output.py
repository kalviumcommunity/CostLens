import os
from typing import Dict, Any

def save_report(summary: Dict[str, Any], output_path: str = "outputs/reports/cost_summary.txt") -> None:
    """
    Formats the processed summary metrics and saves them to a report file.
    
    Responsibilities:
    - Creates parent directories if they don't exist.
    - Generates the text content of the report.
    - Saves the text to the specified output file path.
    - Prints a success message.
    """
    print(f"[Output] Formatting and saving report to {output_path}...")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate the formatted report content
    report_lines = [
        "Cloud Cost Summary Report",
        "=========================",
        f"Total Cost: ${summary['total_cost']:.2f}",
        f"Average Cost: ${summary['average_cost']:.2f}",
        "",
        "Cost by Environment",
        "-------------------"
    ]
    
    for env, cost in summary['cost_by_environment'].items():
        report_lines.append(f"{env}: ${cost:.2f}")
        
    report_content = "\n".join(report_lines) + "\n"
    
    # Write to file
    with open(output_path, "w") as f:
        f.write(report_content)
        
    print(f"[Output] Successfully generated and saved report at: {output_path}")
