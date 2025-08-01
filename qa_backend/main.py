#!/usr/bin/env python3
"""Main script for respiratory data analysis using restructured modules."""

import sys
from pathlib import Path
from typing import Optional

from file_io import read_raw_file
from qa_processing import generate_qa_breath_table, check_qa_table
from csv_export import (
    export_standard_csv, export_developer_csv, 
    STANDARD_COLUMN_MAPPING, DEVELOPER_COLUMN_MAPPING
)


def analyze_respiratory_data(input_file: str, output_dir: Optional[str] = None) -> bool:
    """
    Analyze respiratory data from a raw data file (auto-detects Sensirion or SOTAIRIQ format) and generate QA reports.
    
    Args:
        input_file (str): Path to the input raw data CSV file (Sensirion or SOTAIRIQ format)
        output_dir (Optional[str]): Output directory for results. If None, uses input file directory
        
    Returns:
        bool: True if analysis completed successfully, False otherwise
    """
    try:
        # Set up output directory
        if output_dir is None:
            output_dir = Path(input_file).parent / "output"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Analyzing file: {input_file}")
        print(f"Output directory: {output_path}")
        
        # Step 1: Read the raw data file (auto-detect format)
        print("\n1. Reading raw data file...")
        header_df, breath_table_df, real_data_df = read_raw_file(input_file)
        
        if real_data_df.empty:
            print("Error: No real data found in the file")
            return False
        
        print(f"   - Header rows: {len(header_df)}")
        print(f"   - Breath table rows: {len(breath_table_df)}")
        print(f"   - Real data rows: {len(real_data_df)}")
        
        # Step 2: Generate QA breath table
        print("\n2. Generating QA breath table...")
        qa_table = generate_qa_breath_table(real_data_df)
        
        if qa_table.empty:
            print("Error: No breaths detected in the data")
            return False
        
        print(f"   - Initial breaths detected: {len(qa_table)}")
        
        # Step 3: Check and clean QA table
        print("\n3. Performing QA checks...")
        qa_table_cleaned = check_qa_table(qa_table)
        
        if qa_table_cleaned.empty:
            print("Error: No valid breaths remaining after QA checks")
            return False
        
        # Step 4: Export results
        print("\n4. Exporting results...")
        
        # Generate output filenames
        input_filename = Path(input_file).stem
        standard_filename = f"auto_breath_table_{input_filename}.csv"
        developer_filename = f"dev_auto_breath_table_{input_filename}.csv"
        
        # Export standard CSV
        print("   - Exporting standard CSV...")
        export_standard_csv(qa_table_cleaned, standard_filename, str(output_path))
        
        # Export developer CSV
        print("   - Exporting developer CSV...")
        export_developer_csv(qa_table_cleaned, developer_filename, str(output_path))
        
        print("\n✓ Analysis completed successfully!")
        print(f"\nResults summary:")
        print(f"   - Total breaths analyzed: {len(qa_table_cleaned)}")
        print(f"   - Standard output: {output_path / standard_filename}")
        print(f"   - Developer output: {output_path / developer_filename}")
        
        return True
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        return False


def main():
    """
    Main function to run respiratory data analysis.
    """
    # Example usage - replace with your actual file path
    # Test with SOTAIRIQ format
    raw_file_path = "../rawfile_sample/sotairsample.csv"
    # Test with Sensirion format
    # raw_file_path = "../rawfile_sample/sensirionsample.csv"
    
    # Check if file exists
    if not Path(raw_file_path).exists():
        print(f"Error: File not found: {raw_file_path}")
        print("\nPlease update the raw_file_path variable with the correct path to your data file.")
        sys.exit(1)
    
    # Run analysis
    success = analyze_respiratory_data(raw_file_path)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()