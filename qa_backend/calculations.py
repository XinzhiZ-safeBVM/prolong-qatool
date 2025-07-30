"""Mathematical calculations for respiratory data analysis."""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_volume(time_data: pd.Series, flow_data: pd.Series, 
                    start_index: int, end_index: int) -> float:
    """
    Calculate the volume by integrating flow data between start and end indices.

    Args:
        time_data (pd.Series): Series containing time data
        flow_data (pd.Series): Series containing flow data
        start_index (int): Start index for integration
        end_index (int): End index for integration

    Returns:
        float: Calculated volume in mL

    Raises:
        ValueError: If the data series are not aligned or if indices are invalid
    """
    if len(time_data) != len(flow_data):
        raise ValueError("Time and flow data series must have the same length.")

    if start_index >= end_index:
        raise ValueError("Start index must be less than end index.")

    if start_index < 0 or end_index >= len(time_data):
        raise ValueError("Start or end index out of bounds.")

    # Select data within the specified range
    selected_time = time_data.iloc[start_index:end_index + 1]
    selected_flow = flow_data.iloc[start_index:end_index + 1]

    if len(selected_time) < 2:
        raise ValueError("Not enough data points between start and end for integration.")

    # Perform integration using trapezoidal rule
    volume = np.trapezoid(y=selected_flow, x=selected_time)

    # Convert the volume unit to mL
    volume = volume / 60 * 1000

    return volume


def find_max_in_slice(data: pd.Series, start_index: int, end_index: int) -> float:
    """
    Find the maximum value in a slice of data between start and end indices.

    Args:
        data (pd.Series): Series containing the data
        start_index (int): Start index for the slice
        end_index (int): End index for the slice

    Returns:
        float: Maximum value in the specified slice

    Raises:
        ValueError: If indices are invalid or if the slice is empty
    """
    if start_index >= end_index:
        raise ValueError("Start index must be less than end index.")

    if start_index < data.index.min() or end_index > data.index.max():
        raise ValueError("Start or end index out of bounds.")

    # Select data within the specified range
    selected_data = data.loc[start_index:end_index]

    if selected_data.empty:
        raise ValueError("No data points in the specified range.")

    # Find the maximum value
    max_value = selected_data.max()

    return float(max_value)


def calc_mean_in_slice(data: pd.Series, start_index: int, end_index: int) -> float:
    """
    Calculate the average value in a slice of data between start and end indices.

    Args:
        data (pd.Series): Series containing the data
        start_index (int): Start index for the slice
        end_index (int): End index for the slice

    Returns:
        float: Average value in the specified slice

    Raises:
        ValueError: If indices are invalid or if the slice is empty
    """
    if start_index >= end_index:
        raise ValueError("Start index must be less than end index.")

    if start_index < data.index.min() or end_index > data.index.max():
        raise ValueError("Start or end index out of bounds.")

    # Select data within the specified range
    selected_data = data.loc[start_index:end_index]

    if selected_data.empty:
        raise ValueError("No data points in the specified range.")

    # Calculate the average value
    average_value = selected_data.mean()

    return float(average_value)


def analyze_sotair_single_breath(time_data: pd.Series, flow_data: pd.Series,
                                breath_start: int, insp_end: int, 
                                exp_start: int, breath_end: int) -> Tuple[float, float, bool]:
    """
    Analyze characteristics of a single breath and determine SOTAIR flag.

    Args:
        time_data (pd.Series): Series containing time data
        flow_data (pd.Series): Series containing flow data
        breath_start (int): Index of breath start
        insp_end (int): Index of inspiration end
        exp_start (int): Index of expiration start
        breath_end (int): Index of breath end

    Returns:
        Tuple[float, float, bool]: A tuple containing:
            1. Flow gradient at insp_end point
            2. Time gap between insp_end and exp_start
            3. SOTAIR flag (True if conditions are met, False otherwise)

    Raises:
        ValueError: If there's an issue with the input data or indices
    """
    # Define thresholds as constants
    GRADIENT_THRESHOLD = -1000
    TIME_GAP_THRESHOLD = 0.25

    # Validate indices
    if not (breath_start <= insp_end <= exp_start <= breath_end):
        raise ValueError(
            f"Invalid breath indices: start={breath_start}, insp_end={insp_end}, "
            f"exp_start={exp_start}, end={breath_end}"
        )

    # Calculate minimum flow gradient near insp_end
    if insp_end > breath_start + 3:  # Ensure we have at least 4 points to work with
        gradients = []
        
        # Calculate gradients for three consecutive pairs
        for i in range(3):
            end_idx = insp_end - i
            start_idx = insp_end - (i + 1)
            
            time_diff = time_data.iloc[end_idx] - time_data.iloc[start_idx]
            flow_diff = flow_data.iloc[end_idx] - flow_data.iloc[start_idx]
            
            gradient = flow_diff / time_diff if time_diff != 0 else np.nan
            gradients.append(gradient)
        
        # Get the minimum gradient, ignoring NaN values
        gradient = np.nanmin(gradients) if gradients else np.nan
    else:
        gradient = np.nan

    # Calculate time gap between insp_end and exp_start
    time_gap = time_data.iloc[exp_start] - time_data.iloc[insp_end]

    # Determine SOTAIR flag
    sotair_flag = gradient < GRADIENT_THRESHOLD and time_gap > TIME_GAP_THRESHOLD

    return gradient, time_gap, sotair_flag