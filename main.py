import pandas as pd
from pathlib import Path
from qa_report_tool.analysis import analyze_vt_distribution
from qa_report_tool.report_html import render_html_report
from qa_report_tool.config import DEFAULT_RANGES, DEFAULT_COLUMN

# Import qa_backend modules using proper module path
from qa_backend.file_io import read_sensirion_file
from qa_backend.qa_processing import generate_qa_breath_table, check_qa_table
from qa_backend.csv_export import export_standard_csv

def process_raw_data_and_generate_report(raw_file_path: str, output_dir: str = "output") -> bool:
    """
    Process raw Sensirion CSV file through qa_backend and generate HTML report.
    
    Args:
        raw_file_path (str): Path to the raw Sensirion CSV file
        output_dir (str): Output directory for results
        
    Returns:
        bool: True if processing completed successfully, False otherwise
    """
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing file: {raw_file_path}")
        print(f"Output directory: {output_path}")
        
        # Step 1: Process through qa_backend
        print("\n1. Reading Sensirion file...")
        header_df, breath_table_df, real_data_df = read_sensirion_file(raw_file_path)
        
        if real_data_df.empty:
            print("Error: No real data found in the file")
            return False
        
        print("\n2. Generating QA breath table...")
        qa_table = generate_qa_breath_table(real_data_df)
        
        if qa_table.empty:
            print("Error: No breaths detected in the data")
            return False
        
        print("\n3. Performing QA checks...")
        qa_table_cleaned = check_qa_table(qa_table)
        
        if qa_table_cleaned.empty:
            print("Error: No valid breaths remaining after QA checks")
            return False
        
        # Step 2: Export standard CSV
        print("\n4. Exporting standard CSV...")
        input_filename = Path(raw_file_path).stem
        standard_filename = f"auto_breath_table_{input_filename}.csv"
        export_standard_csv(qa_table_cleaned, standard_filename, str(output_path))
        
        # Step 3: Generate HTML report from the standard CSV
        print("\n5. Generating HTML report...")
        csv_file_path = output_path / standard_filename
        df = pd.read_csv(csv_file_path)
        results = analyze_vt_distribution(df, column=DEFAULT_COLUMN, ranges=DEFAULT_RANGES)
        
        session_id = f"Session_{input_filename}"
        html_output_path = output_path / f"vt_report_{input_filename}.html"
        render_html_report(results, DEFAULT_RANGES, session_id, str(html_output_path))
        
        print("\n✓ Processing completed successfully!")
        print(f"\nResults:")
        print(f"   - Standard CSV: {csv_file_path}")
        print(f"   - HTML Report: {html_output_path}")
        
        return True
        
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return False

def main():
    # Example raw file path - update this with your actual file
    raw_file_path = r"your/path/to/rawfile.csv"
    
    # Check if file exists
    if not Path(raw_file_path).exists():
        print(f"Error: File not found: {raw_file_path}")
        print("\nPlease update the raw_file_path variable with the correct path to your data file.")
        return
    
    # Process the file and generate report
    success = process_raw_data_and_generate_report(raw_file_path)
    
    if not success:
        print("Processing failed!")
    else:
        print("\nAll done! Check the output folder for results.")

if __name__ == "__main__":
    main()