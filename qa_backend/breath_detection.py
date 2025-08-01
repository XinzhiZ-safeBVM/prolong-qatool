"""Breath detection algorithms for respiratory data analysis."""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional


def detect_breaths(df: pd.DataFrame,
                   time_col: str = "Time",
                   flow_col: str = "Flow",
                   pressure_col: str = "Pressure") -> Tuple[List[int], List[int]]:
    """
    Detect breath start and end points in respiratory data using percentage-based thresholds.

    This function analyzes flow and pressure data to identify the start and end points of breaths.
    It uses percentage-based thresholds relative to the maximum values in the data to adapt to
    different baseline conditions. The function accounts for a specific DataFrame structure where
    the first row contains column names and the second row contains units.

    Args:
        df (pd.DataFrame): The input DataFrame containing respiratory data.
        time_col (str): Name of the column containing time data. Default is "Time".
        flow_col (str): Name of the column containing flow data. Default is "Flow".
        pressure_col (str): Name of the column containing pressure data. Default is "Pressure".

    Returns:
        Tuple[List[int], List[int]]: Two lists containing the indices of breath start and end points,
                                     corresponding to the original DataFrame's index.

    Raises:
        ValueError: If required columns are missing or if data conversion fails.
    """
    # Define percentage-based thresholds (as percentages of maximum values)
    positive_flow_threshold_low_pct = 0.05    # 15% of max flow for initial detection
    positive_flow_threshold_high_pct = 0.20   # 35% of max flow for peak validation
    positive_pressure_threshold_pct = 0.10    # 20% of max pressure
    negative_flow_threshold_low_pct = 0.05    # 15% of max flow for end detection
    negative_flow_threshold_high_pct = 0.10   # 25% of max flow for peak validation
    negative_pressure_threshold_pct = 0.05    # 5% of max pressure

    start_points = []
    end_points = []

    # Error handling: Check if required columns exist
    required_columns = [time_col, flow_col, pressure_col]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing one or more required columns: {required_columns}")

    try:
        # Extract data from the third row onwards, preserving the original index
        data_df = df.iloc[2:]

        # Convert columns to numeric, coercing errors to NaN
        flow_data = pd.to_numeric(data_df[flow_col], errors='coerce').values
        pressure_data = pd.to_numeric(data_df[pressure_col], errors='coerce').values

        # Remove NaN values for calculating max values
        flow_clean = flow_data[~np.isnan(flow_data)]
        pressure_clean = pressure_data[~np.isnan(pressure_data)]

        if len(flow_clean) == 0 or len(pressure_clean) == 0:
            raise ValueError("No valid data points found after removing NaN values")

        # Calculate maximum values for percentage-based thresholds
        max_flow = np.max(flow_clean)
        max_pressure = np.max(pressure_clean)

        # Convert percentage thresholds to absolute values
        positive_flow_threshold = (
            max_flow * positive_flow_threshold_low_pct,
            max_flow * positive_flow_threshold_high_pct
        )
        positive_pressure_threshold = max_pressure * positive_pressure_threshold_pct
        negative_flow_threshold = (
            max_flow * negative_flow_threshold_low_pct,
            max_flow * negative_flow_threshold_high_pct
        )
        negative_pressure_threshold = max_pressure * negative_pressure_threshold_pct

        # print(f"Calculated thresholds:")
        # print(f"  Max flow: {max_flow:.3f}")
        # print(f"  Max pressure: {max_pressure:.3f}")
        # print(f"  Positive flow thresholds: {positive_flow_threshold[0]:.3f}, {positive_flow_threshold[1]:.3f}")
        # print(f"  Positive pressure threshold: {positive_pressure_threshold:.3f}")
        # print(f"  Negative flow thresholds: {negative_flow_threshold[0]:.3f}, {negative_flow_threshold[1]:.3f}")
        # print(f"  Negative pressure threshold: {negative_pressure_threshold:.3f}")

    except Exception as e:
        raise ValueError(f"Error in data conversion or threshold calculation: {str(e)}")

    i = 0
    while i < len(data_df) - 50:  # Ensure we have enough data points ahead
        # Check for breath start
        if flow_data[i] > positive_flow_threshold[0]:
            peak_flow = np.nanmax(flow_data[i:i+10])
            peak_pressure = np.nanmax(pressure_data[i:i+10])

            if peak_flow > positive_flow_threshold[1] and peak_pressure > positive_pressure_threshold:
                start_points.append(data_df.index[i])

                # Look for breath end
                j = i + 40
                while j < len(data_df):
                    # Check if average of past 5 points is less than threshold
                    mean_flow = np.nanmean(flow_data[j-5:j])
                    peak_flow = np.nanmax(flow_data[j:j+10])
                    peak_pressure = np.nanmax(pressure_data[j-10:j])

                    if (mean_flow < negative_flow_threshold[0] and
                        peak_flow > negative_flow_threshold[1] and
                        peak_pressure < negative_pressure_threshold):
                        
                        if np.nanmean(flow_data[j:j+10]) < negative_flow_threshold[0]:
                            pass
                        else:
                            end_points.append(data_df.index[j])
                            i = j - 10  # Move main loop to end of this breath
                            break
                    j += 1

                if len(end_points) < len(start_points):
                    # If we didn't find an end point, remove the last start point
                    start_points.pop()

        i += 1

    return start_points, end_points


def detect_single_breath_phases(
    flow_data: pd.Series,
    breath_start: int,
    breath_end: int
) -> Tuple[Optional[int], Optional[int]]:
    """
    Detect inspiration end (insp_end) and expiration start (exp_start) for a single breath,
    then refine insp_end by finding the true start of the low-flow plateau if exp_start is distinct.
    Ensures insp_end <= exp_start.
    
    Args:
        flow_data (pd.Series): Series containing flow data
        breath_start (int): Index of breath start
        breath_end (int): Index of breath end
        
    Returns:
        Tuple[Optional[int], Optional[int]]: Inspiration end and expiration start indices
        
    Raises:
        ValueError: If breath range is invalid
    """

    # === Configurable thresholds and window sizes ===
    INSP_END_SKIP = 21              # samples to skip before searching for insp_end
    INSP_END_PLATEAU_LEN = 5        # look-ahead samples for plateau detection at insp_end
    INSP_END_FLOW_THRESH = 1.0      # SL/min: flow must be below this to mark plateau

    EXP_START_LEN = 5               # samples for exp_start detection window
    EXP_START_FLOW_THRESH = -4.0    # SL/min: negative flow threshold for exp_start

    PLATEAU_REFINE_THRESH = 0.5     # SL/min: flow must be below this for plateau start

    # Validate range
    if breath_start >= breath_end:
        raise ValueError(f"Invalid breath range: start {breath_start} is not before end {breath_end}")

    # 1) Isolate the breath segment by label
    breath_flow = flow_data.loc[breath_start:breath_end]
    idxs = breath_flow.index  # preserve labels

    # 2) Find inspiration end (insp_end)
    insp_end = None
    for i in range(INSP_END_SKIP, len(breath_flow) - INSP_END_PLATEAU_LEN):
        prev_flow = breath_flow.iloc[i - 1]
        curr_flow = breath_flow.iloc[i]
        next_plateau = breath_flow.iloc[i : i + INSP_END_PLATEAU_LEN]
        if (prev_flow > 0
            and curr_flow < INSP_END_FLOW_THRESH
            and all(next_plateau < INSP_END_FLOW_THRESH)):
            insp_end = idxs[i]
            break

    exp_start = None
    if insp_end is not None:
        insp_pos = idxs.get_loc(insp_end)

        # 3) Find expiration start (exp_start)
        for i in range(insp_pos, len(breath_flow) - EXP_START_LEN):
            curr_flow = breath_flow.iloc[i]
            next_flow = breath_flow.iloc[i + 1]
            next_window = breath_flow.iloc[i + 1 : i + 1 + EXP_START_LEN]
            if (curr_flow > EXP_START_FLOW_THRESH
                and next_flow < EXP_START_FLOW_THRESH
                and all(next_window < EXP_START_FLOW_THRESH)):
                exp_start = idxs[i]
                break

        # fallback if no exp_start found
        if exp_start is None:
            exp_start = insp_end

        # 4) Plateau refinement: if exp_start is distinct, adjust insp_end
        if exp_start != insp_end:
            exp_pos = idxs.get_loc(exp_start)
            p = exp_pos
            # move backward until flow exits the low-flow plateau
            while p >= (insp_pos - INSP_END_SKIP + 1) and breath_flow.iloc[p] < PLATEAU_REFINE_THRESH:
                p -= 1
            plateau_pos = p + 1
            # ensure plateau_pos does not exceed exp_pos
            if plateau_pos > exp_pos:
                plateau_pos = exp_pos
            plateau_start = idxs[plateau_pos]
            insp_end = plateau_start

    # final safety: ensure insp_end <= exp_start
    if insp_end is not None and exp_start is not None:
        insp_pos_final = idxs.get_loc(insp_end)
        exp_pos_final = idxs.get_loc(exp_start)
        if insp_pos_final > exp_pos_final:
            insp_end = exp_start

    return insp_end, exp_start


def detect_breath_phases(df: pd.DataFrame, breath_starts: List[int], 
                        breath_ends: List[int], flow_col: str = "Flow") -> Tuple[List[int], List[int]]:
    """
    Detect inspiration end (insp_end) and expiration start (exp_start) points for all breaths.

    Args:
        df (pd.DataFrame): The input DataFrame containing respiratory data
        breath_starts (List[int]): List of breath start indices
        breath_ends (List[int]): List of breath end indices
        flow_col (str): Name of the column containing flow data

    Returns:
        Tuple[List[int], List[int]]: Two lists containing the indices of insp_end and exp_start points

    Raises:
        ValueError: If the flow column is missing, if data conversion fails, 
                   or if no insp_end is found for any breath
    """
    if flow_col not in df.columns:
        raise ValueError(f"Missing flow column: {flow_col}")

    try:
        flow_data = pd.to_numeric(df[flow_col], errors='coerce')
    except Exception as e:
        raise ValueError(f"Error in flow data conversion: {str(e)}")

    insp_end_points = []
    exp_start_points = []

    for start, end in zip(breath_starts, breath_ends):
        insp_end, exp_start = detect_single_breath_phases(flow_data, start, end)

        if insp_end is None:
            print(f"\033[93mWARNING: No inspiration end point found for breath starting at index {start}\033[0m")
            insp_end = start + 1
            exp_start = start + 1

        insp_end_points.append(insp_end)
        exp_start_points.append(exp_start)

    return insp_end_points, exp_start_points


def refine_breath_detection(df: pd.DataFrame, breath_starts: List[int], 
                           breath_ends: List[int], flow_col: str = 'Flow') -> Tuple[List[int], List[int]]:
    """
    Refine breath detection by snapping to a small-threshold crossing near zero.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing respiratory data
        breath_starts (List[int]): List of breath start indices
        breath_ends (List[int]): List of breath end indices
        flow_col (str): Name of the column containing flow data
        
    Returns:
        Tuple[List[int], List[int]]: Refined breath start and end indices
    """
    # Configurable thresholds and window sizes
    ZERO_TOL = 0.5            # SL/min: tolerance around nominal zero
    BACK_WIN_START = 40       # samples to look backward from coarse start
    FWD_WIN_END = 40          # samples to look forward from coarse end

    # Remove first breath if it starts too early
    if breath_starts and breath_starts[0] < 10:
        breath_starts.pop(0)
        breath_ends.pop(0)

    refined_starts = []
    refined_ends = []

    flow = pd.to_numeric(df[flow_col], errors='coerce').values
    N = len(flow)

    for start, end in zip(breath_starts, breath_ends):
        # Refine breath-start by thresholded zero crossing
        lo = max(0, start - BACK_WIN_START)
        for i in range(start - 1, lo - 1, -1):
            f_i = flow[i]
            f_ip = flow[i + 1] if i + 1 < N else None
            # crossing upward past +ZERO_TOL
            if f_ip is not None and f_i <= ZERO_TOL and f_ip >= ZERO_TOL:
                # choose the sample closer to true zero
                refined_starts.append(i if abs(f_i) < abs(f_ip) else i + 1)
                break
        else:
            refined_starts.append(start)

        # Refine breath-end by thresholded zero crossing
        hi = min(N - 1, end + FWD_WIN_END)
        for i in range(end, hi):
            f_i = flow[i]
            f_ip = flow[i + 1] if i + 1 < N else None
            # crossing downward past ZERO_TOL
            if f_ip is not None and f_i >= ZERO_TOL and f_ip <= ZERO_TOL:
                refined_ends.append(i if abs(f_i) < abs(f_ip) else i + 1)
                break
        else:
            refined_ends.append(end)

    return refined_starts, refined_ends