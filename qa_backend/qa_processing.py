"""QA table generation and processing for respiratory data analysis."""

import pandas as pd
import numpy as np
from typing import List, Tuple

# Conditional imports to support both standalone and package usage
try:
    from .breath_detection import (
        detect_breaths, detect_breath_phases, refine_breath_detection
    )
    from .calculations import (
        calculate_volume, find_max_in_slice, calc_mean_in_slice, 
        analyze_sotair_single_breath
    )
except ImportError:
    # Fallback to absolute imports for standalone usage
    from breath_detection import (
        detect_breaths, detect_breath_phases, refine_breath_detection
    )
    from calculations import (
        calculate_volume, find_max_in_slice, calc_mean_in_slice, 
        analyze_sotair_single_breath
    )


def generate_qa_breath_table(real_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a QA breath table from real data.
    
    Args:
        real_data_df (pd.DataFrame): DataFrame containing real respiratory data
        
    Returns:
        pd.DataFrame: QA breath table with calculated metrics
        
    Raises:
        ValueError: If required columns are missing or data processing fails
    """
    try:
        # Step 1: Detect breaths
        breath_starts, breath_ends = detect_breaths(real_data_df)
        
        if not breath_starts or not breath_ends:
            raise ValueError("No breaths detected in the data")
        
        # Step 2: Refine breath detection
        breath_starts, breath_ends = refine_breath_detection(
            real_data_df, breath_starts, breath_ends
        )
        
        # Step 3: Detect breath phases
        insp_ends, exp_starts = detect_breath_phases(
            real_data_df, breath_starts, breath_ends
        )
        
        # Step 4: Calculate breath metrics
        qa_table = _calculate_breath_metrics(
            real_data_df, breath_starts, breath_ends, insp_ends, exp_starts
        )
        
        return qa_table
        
    except Exception as e:
        raise ValueError(f"Error generating QA breath table: {str(e)}")


def _calculate_breath_metrics(df: pd.DataFrame, breath_starts: List[int], 
                             breath_ends: List[int], insp_ends: List[int], 
                             exp_starts: List[int]) -> pd.DataFrame:
    """
    Calculate breath metrics for each detected breath.
    
    Args:
        df (pd.DataFrame): DataFrame containing respiratory data
        breath_starts (List[int]): List of breath start indices
        breath_ends (List[int]): List of breath end indices
        insp_ends (List[int]): List of inspiration end indices
        exp_starts (List[int]): List of expiration start indices
        
    Returns:
        pd.DataFrame: DataFrame with calculated breath metrics
    """
    # Extract data series
    time_data = pd.to_numeric(df['Time'], errors='coerce')
    flow_data = pd.to_numeric(df['Flow'], errors='coerce')
    pressure_data = pd.to_numeric(df['Pressure'], errors='coerce')
    timestamp_data = df['Timestamp']
    
    breath_metrics = []
    
    for i, (start, end, insp_end, exp_start) in enumerate(
        zip(breath_starts, breath_ends, insp_ends, exp_starts), 1
    ):
        try:
            # Basic timing metrics
            breath_start_time = time_data.iloc[start]
            breath_end_time = time_data.iloc[end]
            insp_end_time = time_data.iloc[insp_end]
            exp_start_time = time_data.iloc[exp_start]
            
            # Calculate volumes
            inspiratory_volume = calculate_volume(time_data, flow_data, start, insp_end)
            expiratory_volume = abs(calculate_volume(time_data, flow_data, exp_start, end))
            
            # Calculate peak values
            peak_flow = find_max_in_slice(flow_data, start, insp_end)
            peak_pressure = find_max_in_slice(pressure_data, start, insp_end)
            
            # Calculate mean pressure during inspiration
            mean_pressure_ti = calc_mean_in_slice(pressure_data, start, insp_end)
            
            # Calculate timing metrics
            inspiratory_time = insp_end_time - breath_start_time
            inspiratory_flow_time = insp_end_time - breath_start_time
            
            # SOTAIR analysis
            gradient, time_gap, sotair_flag = analyze_sotair_single_breath(
                time_data, flow_data, start, insp_end, exp_start, end
            )
            
            # Get timestamp
            breath_timestamp = timestamp_data.iloc[start]
            
            breath_metrics.append({
                'breath_number': i,
                'breath_start_time': breath_start_time,
                'insp_stop_time': insp_end_time,
                'exp_start_time': exp_start_time,
                'breath_end_time': breath_end_time,
                'breath_timestamp': breath_timestamp,
                'peak_pressure': peak_pressure,
                'peak_flow': peak_flow,
                'inspiratory_volume': inspiratory_volume,
                'expiratory_volume': expiratory_volume,
                'inspiratory_time': inspiratory_time,
                'inspiratory_flow_time': inspiratory_flow_time,
                'mean_pressure_Ti': mean_pressure_ti,
                'sotair': sotair_flag,
                'gradient': gradient,
                'time_gap': time_gap
            })
            
        except Exception as e:
            print(f"Warning: Error calculating metrics for breath {i}: {str(e)}")
            continue
    
    return pd.DataFrame(breath_metrics)


def check_qa_table(qa_breath_table: pd.DataFrame) -> pd.DataFrame:
    """
    Check and clean the QA breath table by applying various validation criteria.
    Currently checks:
    - Removes rows with expiratory volume greater than REAL_POSITIVE threshold
    - Removes rows with inspiratory volume less than REAL_NEGATIVE threshold
    - Reassigns breath numbers sequentially

    Args:
        qa_breath_table (pd.DataFrame): The QA breath table generated by generate_qa_breath_table()

    Returns:
        pd.DataFrame: A cleaned DataFrame with invalid rows removed and breath numbers reassigned
    """
    # Define thresholds
    REAL_POSITIVE = 2000  # mL - maximum reasonable expiratory volume
    REAL_NEGATIVE = 50    # mL - minimum reasonable inspiratory volume
    
    if qa_breath_table.empty:
        return qa_breath_table
    
    # Create a copy to avoid modifying the original
    cleaned_table = qa_breath_table.copy()
    
    # Track original count
    original_count = len(cleaned_table)
    
    # Remove breaths with unrealistic expiratory volumes
    if 'expiratory_volume' in cleaned_table.columns:
        mask_exp = cleaned_table['expiratory_volume'] <= REAL_POSITIVE
        cleaned_table = cleaned_table[mask_exp]
        exp_removed = original_count - len(cleaned_table)
        if exp_removed > 0:
            print(f"Removed {exp_removed} breaths with expiratory volume > {REAL_POSITIVE} mL")
    
    # Remove breaths with unrealistic inspiratory volumes
    if 'inspiratory_volume' in cleaned_table.columns:
        mask_insp = cleaned_table['inspiratory_volume'] >= REAL_NEGATIVE
        current_count = len(cleaned_table)
        cleaned_table = cleaned_table[mask_insp]
        insp_removed = current_count - len(cleaned_table)
        if insp_removed > 0:
            print(f"Removed {insp_removed} breaths with inspiratory volume < {REAL_NEGATIVE} mL")
    
    # Reassign breath numbers sequentially
    if 'breath_number' in cleaned_table.columns and not cleaned_table.empty:
        cleaned_table = cleaned_table.reset_index(drop=True)
        cleaned_table['breath_number'] = range(1, len(cleaned_table) + 1)
    
    final_count = len(cleaned_table)
    total_removed = original_count - final_count
    
    if total_removed > 0:
        print(f"QA Check Summary: Removed {total_removed} of {original_count} breaths. "
              f"{final_count} breaths remaining.")
    else:
        print(f"QA Check Summary: All {original_count} breaths passed validation.")
    
    return cleaned_table


def refine_qa_breath_table(real_data_df: pd.DataFrame, 
                          user_breath_table_df: pd.DataFrame) -> pd.DataFrame:
    """
    Refine QA breath table using user-provided breath table as reference.
    
    Args:
        real_data_df (pd.DataFrame): DataFrame containing real respiratory data
        user_breath_table_df (pd.DataFrame): User-provided breath table for reference
        
    Returns:
        pd.DataFrame: Refined QA breath table
        
    Raises:
        ValueError: If required columns are missing or data processing fails
    """
    try:
        # Extract breath timing from user table
        if 'Time (s)' not in user_breath_table_df.columns:
            raise ValueError("User breath table must contain 'Time (s)' column")
        
        user_breath_times = user_breath_table_df['Time (s)'].tolist()
        
        # Convert to indices in real data
        time_data = pd.to_numeric(real_data_df['Time'], errors='coerce')
        
        breath_starts = []
        breath_ends = []
        
        for i, breath_time in enumerate(user_breath_times[:-1]):
            # Find closest index for current breath time
            start_idx = (time_data - breath_time).abs().idxmin()
            
            # Find closest index for next breath time
            next_breath_time = user_breath_times[i + 1]
            end_idx = (time_data - next_breath_time).abs().idxmin()
            
            breath_starts.append(start_idx)
            breath_ends.append(end_idx)
        
        # Detect breath phases
        insp_ends, exp_starts = detect_breath_phases(
            real_data_df, breath_starts, breath_ends
        )
        
        # Calculate breath metrics
        qa_table = _calculate_breath_metrics(
            real_data_df, breath_starts, breath_ends, insp_ends, exp_starts
        )
        
        return qa_table
        
    except Exception as e:
        raise ValueError(f"Error refining QA breath table: {str(e)}")