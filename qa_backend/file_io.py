"""File I/O operations for respiratory data analysis."""

import pandas as pd
import sys
from typing import Tuple
from io import StringIO


def read_sensirion_file(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads a Sensirion file (legacy format) and returns three pandas DataFrames:
    header_df, breath_table_df, and real_data_df.
    
    Args:
        filepath (str): Path to the Sensirion CSV file
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Header data, breath table, and real data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    try:
        with open(filepath, newline='', encoding="utf-8") as csvfile:
            file_content = csvfile.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading file {filepath}: {str(e)}")

    # Initialize variables
    headers = []
    breath_table_start = None
    data_start = None

    # Find the start of breath table and data
    for i, line in enumerate(file_content):
        if line.startswith("Breath Count,Time (s)"):
            breath_table_start = i
        elif line.startswith("Time,Timestamp,Flow,Pressure"):
            data_start = i
            break
        if breath_table_start is None:
            headers.append(line.strip().split(','))

    # Create header DataFrame
    header_df = pd.DataFrame(headers)

    # Create breath table DataFrame
    if breath_table_start is not None and data_start is not None:
        breath_table_df = pd.read_csv(
            filepath, 
            skiprows=breath_table_start, 
            nrows=data_start - breath_table_start - 1
        )
    else:
        breath_table_df = pd.DataFrame()

    # Create real data DataFrame
    if data_start is not None:
        # Read column names and units
        column_names = file_content[data_start].strip().split(',')
        column_units = file_content[data_start + 1].strip().split(',')

        # Read the actual data
        real_data_df = pd.read_csv(filepath, skiprows=data_start + 2, names=column_names)

        # Add units as a new row at the top of the DataFrame
        real_data_df.loc[-1] = column_units
        real_data_df.index = real_data_df.index + 1
        real_data_df = real_data_df.sort_index()

        # Convert columns to appropriate types
        real_data_df = _convert_column_types(real_data_df)
    else:
        real_data_df = pd.DataFrame()

    # Check for TSI device
    _check_tsi_device(header_df)

    return header_df, breath_table_df, real_data_df


def _convert_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame columns to appropriate data types.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with converted column types
    """
    for column in df.columns:
        if column == "Note":
            df.loc[1:, column] = df.loc[1:, column].astype(str)
        elif column == "Timestamp":
            # Convert ISO 8601 format timestamp with milliseconds and UTC timezone
            df.loc[1:, column] = pd.to_datetime(
                df.loc[1:, column],
                format='%Y-%m-%dT%H:%M:%S.%fZ',
                utc=True
            )
        elif column in ["start_flag", "stop_flag", "Breath Count"]:
            df.loc[1:, column] = pd.to_numeric(
                df.loc[1:, column], errors='coerce'
            ).astype('Int64')
        else:
            df.loc[1:, column] = pd.to_numeric(df.loc[1:, column], errors='coerce')
    
    return df


def read_raw_file(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Automatically detect file format and read raw data file using the appropriate parser.
    
    This function detects whether the file is in the old Sensirion format or the new SOTAIRIQ format
    and calls the appropriate parsing function.
    
    Args:
        filepath (str): Path to the raw data CSV file
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Header/conclusion data, breath table, and raw data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is not recognized or invalid
    """
    try:
        # Read first few lines to detect format
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()[:1000]  # Read first 1000 lines for detection
        
        file_content = ''.join(lines)
        
        # Check for new SOTAIRIQ format indicators
        if ('breaths,time_s,bpm' in file_content and 
            'ts_ms,flow_slm,press_cmH2O,trig' in file_content):
            print(f"Detected new SOTAIRIQ format for file: {filepath}")
            return read_sotairiq_file(filepath)
        
        # Check for old Sensirion format indicators (more flexible matching)
        elif (('Breath Count,Time (s)' in file_content or 'Breath Count' in file_content) and 
              'Time,Timestamp,Flow,Pressure' in file_content):
            print(f"Detected legacy Sensirion format for file: {filepath}")
            return read_sensirion_file(filepath)
        
        else:
            raise ValueError(f"Unknown file format. File does not match known Sensirion or SOTAIRIQ formats: {filepath}")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error detecting file format for {filepath}: {str(e)}")


def read_sotairiq_file(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads a SOTAIRIQ file (new format) and returns three pandas DataFrames:
    header_df (conclusion table), breath_table_df (breath summary), and real_data_df (raw data).
    
    The new file format contains four tables:
    1. Conclusion table (breaths, time_s, bpm)
    2. Breath summary table (breath, ts_ms, ...)
    3. SOTAIR events table (sotrig, ts_ms, ...) - optional
    4. Raw data table (ts_ms, flow_slm, press_cmH2O, trig)
    
    Args:
        filepath (str): Path to the SOTAIRIQ CSV file
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Conclusion data, breath table, and raw data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    try:
        # Extract each table using the StringIO approach
        header_df = _extract_table_by_header(filepath, 'breaths,time_s,bpm')
        breath_table_df = _extract_table_by_header(filepath, 'breath,ts_ms,in_flow_time_s')
        raw_data_df = _extract_table_by_header(filepath, 'ts_ms,flow_slm,press_cmH2O,trig')
        
        # Handle missing tables
        if header_df is None:
            header_df = pd.DataFrame()
        if breath_table_df is None:
            breath_table_df = pd.DataFrame()
        if raw_data_df is None:
            raw_data_df = pd.DataFrame()
        
        # Process raw data to match expected format
        if not raw_data_df.empty:
            # Convert timestamp from ms to seconds
            if 'ts_ms' in raw_data_df.columns:
                raw_data_df['Time'] = raw_data_df['ts_ms'] / 1000.0
                # Rename columns to match expected format
                raw_data_df = raw_data_df.rename(columns={
                    'flow_slm': 'Flow',
                    'press_cmH2O': 'Pressure',
                    'ts_ms': 'Timestamp'
                })
            
            # Convert columns to appropriate types
            raw_data_df = _convert_column_types_new_format(raw_data_df)
        
        # Process breath table to add Time column
        if not breath_table_df.empty and 'ts_ms' in breath_table_df.columns:
            breath_table_df['Time'] = breath_table_df['ts_ms'] / 1000.0
        
        return header_df, breath_table_df, raw_data_df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading SOTAIRIQ file {filepath}: {str(e)}")


def _extract_table_by_header(csv_file_path: str, header_start: str) -> pd.DataFrame:
    """Extract a table from CSV file by finding its header and reading until empty line."""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Find the start of table
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith(header_start):
                start_idx = i
                break
        
        if start_idx is None:
            return None
        
        # Find the end (first empty line after the header)
        end_idx = None
        for i in range(start_idx + 1, len(lines)):
            if lines[i].strip() == '':
                end_idx = i
                break
        
        # If no empty line found, read to end of file
        if end_idx is None:
            end_idx = len(lines)
        
        # Extract the table section
        table_lines = lines[start_idx:end_idx]
        
        # Convert to DataFrame using StringIO
        table_data = pd.read_csv(StringIO(''.join(table_lines)))
        
        return table_data
        
    except Exception:
        return None


def _convert_column_types_new_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame columns to appropriate data types for new file format.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with converted column types
    """
    for column in df.columns:
        if column == "trig":
            # Keep trig column as string/object type
            df[column] = df[column].astype(str)
        elif column in ["Timestamp", "ts_ms"]:
            # Convert timestamp columns to numeric (milliseconds)
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif column in ["Time", "Flow", "Pressure"]:
            # Convert numeric columns
            df[column] = pd.to_numeric(df[column], errors='coerce')
        else:
            # Default to numeric conversion for other columns
            df[column] = pd.to_numeric(df[column], errors='coerce')
    
    return df


def _check_tsi_device(header_df: pd.DataFrame) -> None:
    """
    Check if the file indicates a TSI device and warn the user.
    
    Args:
        header_df (pd.DataFrame): Header DataFrame to check
    """
    if not header_df.empty and "Device Name" in header_df[0].values:
        device_name_row = header_df[header_df[0] == "Device Name"].iloc[0]
        if len(device_name_row) > 1 and "TSI" in device_name_row[1]:
            sys.stderr.write("File indicates TSI device. Please use the ReadTsiFile.\n")


# Testing code
if __name__ == "__main__":
    print("Testing file_io functions...")
    print("=" * 50)
    
    # Test files
    test_files = [
        "../rawfile_sample/sotairsample.csv",  # SOTAIRIQ format
        "../rawfile_sample/sensirionsample.csv"  # Sensirion format
    ]
    
    import os
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Testing file: {test_file}")
        print(f"File exists: {os.path.exists(test_file)}")
        
        if not os.path.exists(test_file):
            print(f"Skipping {test_file} - file not found")
            continue
            
        try:
            # Test the unified read_raw_file function
            print(f"\nTesting read_raw_file (auto-detection):")
            header_df, breath_df, raw_df = read_raw_file(test_file)
            
            print(f"\nResults:")
            print(f"  Header/Conclusion DataFrame:")
            print(f"    Shape: {header_df.shape}")
            print(f"    Columns: {list(header_df.columns)}")
            if not header_df.empty:
                print(f"    Sample data:\n{header_df.head(2)}")
            
            print(f"\n  Breath DataFrame:")
            print(f"    Shape: {breath_df.shape}")
            print(f"    Columns: {list(breath_df.columns)}")
            if not breath_df.empty:
                print(f"    First 2 rows:\n{breath_df.head(2)}")
            
            print(f"\n  Raw Data DataFrame:")
            print(f"    Shape: {raw_df.shape}")
            print(f"    Columns: {list(raw_df.columns)}")
            if not raw_df.empty:
                print(f"    First 2 rows:\n{raw_df.head(2)}")
                print(f"    Data types:\n{raw_df.dtypes}")
            
        except Exception as e:
            print(f"Error testing file {test_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Testing completed.")