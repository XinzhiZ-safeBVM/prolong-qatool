"""CSV export functionality for respiratory data analysis."""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, Optional


# Standard column mappings
STANDARD_COLUMN_MAPPING = {
    'breath_number': {'new_name': 'Breath Number', 'unit': 'count'},
    'peak_pressure': {'new_name': 'Peak Pressure', 'unit': 'cmH2O'},
    'peak_flow': {'new_name': 'Peak Flow', 'unit': 'L/min'},
    'inspiratory_volume': {'new_name': 'Inhaled Tidal Volume', 'unit': 'mL'},
    'expiratory_volume': {'new_name': 'Exhaled Tidal Volume', 'unit': 'mL'},
    'inspiratory_time': {'new_name': 'Inspiratory Time', 'unit': 's'},
    'inspiratory_flow_time': {'new_name': 'Inspiratory Flow Time', 'unit': 's'},
    'sotair': {'new_name': 'SOTAIR Activation', 'unit': '0/1'}
}

DEVELOPER_COLUMN_MAPPING = {
    'breath_number': {'new_name': 'Breath Number', 'unit': 'count'},
    'peak_pressure': {'new_name': 'Peak Pressure', 'unit': 'cmH2O'},
    'peak_flow': {'new_name': 'Peak Flow', 'unit': 'L/min'},
    'inspiratory_volume': {'new_name': 'Inhaled Tidal Volume', 'unit': 'mL'},
    'expiratory_volume': {'new_name': 'Exhaled Tidal Volume', 'unit': 'mL'},
    'inspiratory_time': {'new_name': 'Inspiratory Time', 'unit': 's'},
    'inspiratory_flow_time': {'new_name': 'Inspiratory Flow Time', 'unit': 's'},
    'mean_pressure_Ti': {'new_name': 'Mean Pressure During Inspiration', 'unit': 'cmH2O'},
    'sotair': {'new_name': 'SOTAIR Activation', 'unit': '0/1'},
    'breath_start_time': {'new_name': 'Breath Start Time', 'unit': 's'},
    'insp_stop_time': {'new_name': 'Inspiratory Stop Time', 'unit': 's'},
    'exp_start_time': {'new_name': 'Expiratory Start Time', 'unit': 's'},
    'breath_end_time': {'new_name': 'Breath End Time', 'unit': 's'},
    'breath_timestamp': {'new_name': 'Breath Timestamp', 'unit': 'datetime'}
}


def generate_custom_csv(qa_breath_table: pd.DataFrame, output_filename: str, 
                       column_mapping: Dict[str, Dict[str, str]], 
                       output_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Generate a custom CSV file from the QA breath table with specified column mapping.
    
    Args:
        qa_breath_table (pd.DataFrame): The QA breath table to export
        output_filename (str): Name of the output CSV file
        column_mapping (Dict[str, Dict[str, str]]): Mapping of original columns to new names and units
        output_dir (Optional[str]): Output directory path. If None, uses current directory
        
    Returns:
        pd.DataFrame: The processed DataFrame that was saved to CSV
        
    Raises:
        ValueError: If the QA breath table is empty or required columns are missing
        OSError: If there's an error creating the output directory or writing the file
    """
    if qa_breath_table.empty:
        raise ValueError("QA breath table is empty")
    
    # Create output directory if specified
    if output_dir:
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise OSError(f"Error creating output directory {output_dir}: {str(e)}")
    
    # Create a copy of the table to avoid modifying the original
    processed_table = qa_breath_table.copy()
    
    # Apply column mapping
    processed_table = _apply_column_mapping(processed_table, column_mapping)
    
    # Construct full output path
    if output_dir:
        output_path = Path(output_dir) / output_filename
    else:
        output_path = Path(output_filename)
    
    try:
        # Save to CSV
        processed_table.to_csv(output_path, index=False)
        print(f"Successfully saved CSV to: {output_path}")
        
    except Exception as e:
        raise OSError(f"Error writing CSV file {output_path}: {str(e)}")
    
    return processed_table


def _apply_column_mapping(df: pd.DataFrame, 
                         column_mapping: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    """
    Apply column mapping to rename columns and add units row.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        column_mapping (Dict[str, Dict[str, str]]): Column mapping configuration
        
    Returns:
        pd.DataFrame: DataFrame with renamed columns and units row
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Filter columns that exist in both the DataFrame and the mapping
    available_columns = [col for col in column_mapping.keys() if col in result_df.columns]
    
    if not available_columns:
        print("Warning: No columns from the mapping found in the DataFrame")
        return result_df
    
    # Select only the mapped columns
    result_df = result_df[available_columns]
    
    # Convert boolean SOTAIR values to 0/1 before renaming
    if 'sotair' in result_df.columns:
        result_df['sotair'] = result_df['sotair'].astype(int)
    
    # Rename columns
    rename_mapping = {
        col: column_mapping[col]['new_name'] 
        for col in available_columns
    }
    result_df = result_df.rename(columns=rename_mapping)
    
    # Create units row
    units_row = {
        column_mapping[col]['new_name']: column_mapping[col]['unit']
        for col in available_columns
    }
    
    # Insert units row at the top
    units_df = pd.DataFrame([units_row])
    result_df = pd.concat([units_df, result_df], ignore_index=True)
    
    return result_df


def export_standard_csv(qa_breath_table: pd.DataFrame, output_filename: str, 
                       output_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Export QA breath table using standard column mapping.
    
    Args:
        qa_breath_table (pd.DataFrame): The QA breath table to export
        output_filename (str): Name of the output CSV file
        output_dir (Optional[str]): Output directory path
        
    Returns:
        pd.DataFrame: The processed DataFrame that was saved to CSV
    """
    return generate_custom_csv(
        qa_breath_table, output_filename, STANDARD_COLUMN_MAPPING, output_dir
    )


def export_developer_csv(qa_breath_table: pd.DataFrame, output_filename: str, 
                        output_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Export QA breath table using developer column mapping (includes all available columns).
    
    Args:
        qa_breath_table (pd.DataFrame): The QA breath table to export
        output_filename (str): Name of the output CSV file
        output_dir (Optional[str]): Output directory path
        
    Returns:
        pd.DataFrame: The processed DataFrame that was saved to CSV
    """
    return generate_custom_csv(
        qa_breath_table, output_filename, DEVELOPER_COLUMN_MAPPING, output_dir
    )


def create_custom_mapping(columns_config: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Create a custom column mapping configuration.
    
    Args:
        columns_config (Dict[str, Dict[str, str]]): Custom column configuration
        
    Returns:
        Dict[str, Dict[str, str]]: Validated column mapping
        
    Example:
        >>> config = {
        ...     'breath_number': {'new_name': 'Breath ID', 'unit': 'count'},
        ...     'peak_pressure': {'new_name': 'Max Pressure', 'unit': 'cmH2O'}
        ... }
        >>> mapping = create_custom_mapping(config)
    """
    validated_mapping = {}
    
    for col, config in columns_config.items():
        if not isinstance(config, dict):
            raise ValueError(f"Configuration for column '{col}' must be a dictionary")
        
        if 'new_name' not in config or 'unit' not in config:
            raise ValueError(f"Configuration for column '{col}' must contain 'new_name' and 'unit'")
        
        validated_mapping[col] = {
            'new_name': str(config['new_name']),
            'unit': str(config['unit'])
        }
    
    return validated_mapping