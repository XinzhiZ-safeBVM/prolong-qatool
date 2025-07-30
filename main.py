import pandas as pd
from qa_report_tool.analysis import analyze_vt_distribution
from qa_report_tool.report_html import render_html_report
from qa_report_tool.config import DEFAULT_RANGES, DEFAULT_COLUMN

def main():
    file_path = "your_csv_path.csv"  # Replace this with your actual file
    session_id = "Session_001"
    output_path = "vt_report.html"

    df = pd.read_csv(file_path)
    results = analyze_vt_distribution(df, column=DEFAULT_COLUMN, ranges=DEFAULT_RANGES)
    render_html_report(results, DEFAULT_RANGES, session_id, output_path)

if __name__ == "__main__":
    main()