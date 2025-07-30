"""File I/O operations for respiratory data analysis."""

import pandas as pd
import sys
from typing import Tuple


def read_sensirion_file(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads a Sensirion file and returns three pandas DataFrames:
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