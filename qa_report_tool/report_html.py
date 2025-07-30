import json
from datetime import datetime
from typing import Dict, List, Tuple

def render_html_report(
    results: Dict[str, float],
    ranges: List[Tuple[float, float]],
    session_id: str,
    output_path: str
):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    core_stats = f"""
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Breath Count</td><td>{results['Total Breath Count']}</td></tr>
        <tr><td>Breaths Per Minute</td><td>{results.get('Breaths Per Minute', float('nan')):.2f}</td></tr>
        <tr><td>Max Inhaled Tidal Volume (mL)</td><td>{results['Max Inhaled Tidal Volume']:.2f}</td></tr>
        <tr><td>Min Inhaled Tidal Volume (mL)</td><td>{results['Min Inhaled Tidal Volume']:.2f}</td></tr>
        <tr><td>Percentage of Breaths with Vt in [400, 600] mL</td><td>{results['Pct Vt in [400, 600]']:.2f}%</td></tr>
        <tr><td>Percentage of Breaths with Vt &lt; 400 mL</td><td>{results.get('Pct Vt < 400', 0):.2f}%</td></tr>
        <tr><td>Percentage of Breaths with Vt &gt; 600 mL</td><td>{results.get('Pct Vt > 600', 0):.2f}%</td></tr>
    </table>
    """

    range_rows = []
    bar_labels = []
    bar_values = []

    for low, high in ranges:
        if low is None and high is not None:
            label = f'Percentage of Breaths with Vt < {high}'
            key = f'Pct Vt < {high}'
        elif low is not None and high is None:
            label = f'Percentage of Breaths with Vt > {low}'
            key = f'Pct Vt > {low}'
        else:
            label = f'Percentage of Breaths with Vt in [{low}, {high}]'
            key = f'Pct Vt in [{low}, {high}]'
        val = results.get(key, float('nan'))
        range_rows.append(f"<tr><td>{label}</td><td>{val:.2f}%</td></tr>")
        bar_labels.append(label.replace("Percentage of Breaths with ", ""))
        bar_values.append(round(val, 2))

    range_table = f"""
    <table>
        <tr><th>Range</th><th>Percentage</th></tr>
        {''.join(range_rows)}
    </table>
    """

    bar_chart = f"""
    <div id="plotly-chart"></div>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <script>
        var data = [{{
            x: {json.dumps(bar_labels)},
            y: {json.dumps(bar_values)},
            type: 'bar',
            marker: {{
                color: 'rgba(58,71,80,0.6)',
                line: {{
                    color: 'rgba(58,71,80,1.0)',
                    width: 1.5
                }}
            }}
        }}];
        var layout = {{
            title: 'Tidal Volume Distribution by Range',
            xaxis: {{ title: 'Range' }},
            yaxis: {{ title: 'Percentage of Breaths', range: [0, 100] }}
        }};
        Plotly.newPlot('plotly-chart', data, layout);
    </script>
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inhaled Tidal Volume Report - {session_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
            }}
            table {{
                border-collapse: collapse;
                width: 70%;
                margin-bottom: 30px;
            }}
            th, td {{
                border: 1px solid #999;
                padding: 8px 12px;
                text-align: center;
            }}
            th {{
                background-color: #f0f0f0;
            }}
            h1 {{
                color: #2c3e50;
            }}
        </style>
    </head>
    <body>
        <h1>Inhaled Tidal Volume Report</h1>
        <p><strong>Session ID:</strong> {session_id}<br>
           <strong>Generated:</strong> {now}</p>
        <h2>Bar Chart Visualization</h2>
        {bar_chart}
        <h2>Summary Statistics</h2>
        {core_stats}
        <h2>Tidal Volume Distribution by Range</h2>
        {range_table}
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML report saved to {output_path}")