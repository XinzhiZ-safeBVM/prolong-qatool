# Prolong Report Tool GUI Application

A simple tkinter-based graphical user interface for the Prolong Report Tool CSV analysis.

## Features

- **File Picker**: Easy selection of raw CSV files (Sensirion or SOTAIRIQ format)
- **One-Click Analysis**: Run the complete analysis pipeline with a single button
- **Real-time Output**: View processing progress and messages in real-time
- **Automatic Report Opening**: HTML reports are automatically opened in your default browser
- **Version Tracking**: Displays git commit hash for version identification
- **Smart Output Location**: Creates `html_report` folder next to your CSV file
- **User-Friendly Interface**: Clean and intuitive design

## How to Use

1. **Launch the GUI**:
   ```bash
   python gui_main.py
   ```

2. **Select a CSV File**:
   - Click the "Browse" button
   - Navigate to your raw CSV file (typically in the `rawfile_sample` folder)
   - Select the file you want to analyze

3. **Run Analysis**:
   - Click the "Run Analysis" button
   - Watch the processing output in the text area
   - The analysis will automatically:
     - Process the raw data
     - Generate QA breath table
     - Perform quality checks
     - Export standard CSV
     - Generate HTML report
     - Open the report in your browser

4. **View Results**:
   - The HTML report will open automatically in your default browser
   - CSV files are saved in the `output` folder
   - All processing messages are displayed in the GUI

## GUI Components

- **File Selection**: Browse and select input CSV files
- **Run Analysis Button**: Starts the analysis process
- **Processing Output**: Real-time display of analysis progress
- **Status Bar**: Shows current application status

## Output Files

The GUI generates the same output files as the command-line version:
- `auto_breath_table_[filename].csv` - Processed breath data
- `vt_report_[filename].html` - Interactive HTML report

All files are saved in an `html_report` folder created next to your selected CSV file.

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- All dependencies from the main QA Tool project

## Error Handling

- File validation before processing
- Real-time error messages in the output area
- User-friendly error dialogs
- Graceful handling of processing failures

## Notes

- The GUI runs the analysis in a separate thread to keep the interface responsive
- Processing output is captured and displayed in real-time
- The interface is disabled during processing to prevent multiple simultaneous runs
- HTML reports are automatically opened using the system's default browser