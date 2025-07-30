import pandas as pd
from typing import Dict, List, Tuple

def analyze_vt_distribution(
    df: pd.DataFrame,
    column: str = "Inhaled Tidal Volume",
    ranges: List[Tuple[float, float]] = [(None, 400), (400, 600), (600, None)],
    total_time_seconds: float = None
) -> Dict[str, float]:
    try:
        vt = pd.to_numeric(df.iloc[1:][column], errors='coerce').dropna()
        total = len(vt)
        
        # Calculate Breaths Per Minute using total recording time
        bpm = float('nan')
        if total > 0 and total_time_seconds is not None and total_time_seconds > 0:
            total_time_minutes = total_time_seconds / 60
            bpm = total / total_time_minutes
        
        result = {
            'Total Breath Count': total,
            'Max Inhaled Tidal Volume': vt.max() if total > 0 else float('nan'),
            'Min Inhaled Tidal Volume': vt.min() if total > 0 else float('nan'),
            'Breaths Per Minute': bpm
        }

        # Always include 400–600 range and fixed <400, >600 ranges
        if total > 0:
            in_400_600 = vt.between(400, 600, inclusive='both')
            result['Pct Vt in [400, 600]'] = (in_400_600.sum() / total) * 100
            result['Pct Vt < 400'] = ((vt < 400).sum() / total) * 100
            result['Pct Vt > 600'] = ((vt > 600).sum() / total) * 100
        else:
            result['Pct Vt in [400, 600]'] = float('nan')
            result['Pct Vt < 400'] = float('nan')
            result['Pct Vt > 600'] = float('nan')

        for low, high in ranges:
            if low is None and high is not None:
                mask = vt < high
                label = f'Pct Vt < {high}'
            elif low is not None and high is None:
                mask = vt > low
                label = f'Pct Vt > {low}'
            else:
                mask = (vt >= low) & (vt <= high)
                label = f'Pct Vt in [{low}, {high}]'
            result[label] = mask.sum() / total * 100 if total > 0 else float('nan')

        return result
    except Exception as e:
        print(f"Error in analyze_vt_distribution: {str(e)}")
        fallback = {
            'Total Breath Count': float('nan'),
            'Max Inhaled Tidal Volume': float('nan'),
            'Min Inhaled Tidal Volume': float('nan'),
            'Breaths Per Minute': float('nan'),
            'Pct Vt in [400, 600]': float('nan'),
            'Pct Vt < 400': float('nan'),
            'Pct Vt > 600': float('nan')
        }
        for low, high in ranges:
            if low is None and high is not None:
                label = f'Pct Vt < {high}'
            elif low is not None and high is None:
                label = f'Pct Vt > {low}'
            else:
                label = f'Pct Vt in [{low}, {high}]'
            fallback[label] = float('nan')
        return fallback