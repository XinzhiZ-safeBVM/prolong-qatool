# Respiratory Data Analysis & QA Report Tool

A comprehensive Python toolkit for analyzing respiratory data from multiple device formats, generating quality assurance (QA) breath tables, and creating detailed HTML reports with tidal volume distribution analysis.

## 🚀 Features

- **Complete End-to-End Pipeline**: Raw CSV → QA Analysis → Standard CSV → HTML Report
- **Multi-Format Support**: Auto-detects Sensirion and SOTAIRIQ file formats
- **Modular Architecture**: Separate packages for backend processing and report generation
- **Breath Detection & Analysis**: Advanced algorithms for detecting breath phases and calculating respiratory metrics
- **Quality Assurance**: Automated validation and cleaning of breath data
- **Multiple Output Formats**: Standard CSV, Developer CSV, and interactive HTML reports
- **SOTAIR Analysis**: Specialized analysis for SOTAIR activation detection
- **Configurable Parameters**: Easily adjustable thresholds and settings
- **Breaths Per Minute Calculation**: Accurate BPM calculation using total recording time

## 📁 Project Structure

```
prolong-qatool/
├── main.py                    # Integrated pipeline (Raw CSV → HTML Report)
├── gui_main.py               # GUI application with tkinter interface
├── GUI_README.md             # GUI usage documentation
├── SETUP_GUIDE.md            # Complete setup & build guide
├── requirements.txt          # Python dependencies
├── build_exe.py              # PyInstaller build script
├── build.bat                 # Windows build batch file
├── qa_backend/                # Core respiratory data processing
│   ├── main.py               # Standalone QA analysis tool
│   ├── file_io.py            # Multi-format file reading (Sensirion/SOTAIRIQ)
│   ├── breath_detection.py   # Breath detection algorithms
│   ├── calculations.py       # Volume, flow, and SOTAIR calculations
│   ├── qa_processing.py      # QA table generation and validation
│   ├── csv_export.py         # CSV export with custom formatting
│   └── config.py             # Configuration parameters
├── qa_report_tool/           # HTML report generation
│   ├── analysis.py           # Tidal volume distribution analysis
│   ├── report_html.py        # HTML report rendering
│   └── config.py             # Report configuration
└── rawfile_sample/           # Sample CSV files for testing
    ├── [Sensirion format samples]
    └── [SOTAIRIQ format samples]
```

## 🛠️ Installation

### Quick Start
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete step-by-step instructions including:
- Conda environment setup
- Dependency installation
- Building executables
- Distribution guide

### Prerequisites
- Python 3.12 (Anaconda/Miniconda recommended)
- Git (for version tracking)
- Windows 10/11

### Quick Setup
```bash
# Create conda environment
conda create -n prolong-report-tool python=3.12
conda activate prolong-report-tool

# Install dependencies
pip install -r requirements.txt

# Test the application
python gui_main.py
```

## 📖 Usage

### Option 1: GUI Application (Easiest)

Use the graphical user interface for the simplest experience:

```bash
python gui_main.py
```

**Features:**
- File picker to select CSV files
- One-click analysis with "Run Analysis" button
- Real-time processing output display
- Automatic HTML report opening in browser
- Version tracking with git commit hash
- Smart output location (creates `html_report` folder next to CSV file)
- User-friendly interface with progress tracking

See [GUI_README.md](GUI_README.md) for detailed GUI usage instructions.

### Building Standalone Executable

Create a standalone .exe file for distribution:

```bash
# Quick build (Windows)
build.bat

# Or manual build
python build_exe.py
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed build instructions and distribution guide.

### Option 2: Integrated Pipeline (Command Line)

Process raw respiratory data and generate complete analysis in one step:

#### Step 1: Configure Your Data File

Edit the `raw_file_path` variable in `main.py` to point to your data file:

```python
# In main.py, update this line (around line 91):
raw_file_path = "rawfile_sample/your_data_file.csv"

# Examples of supported file paths:
# For SOTAIRIQ format:
raw_file_path = "rawfile_sample/sotairsample.csv"

# For Sensirion format:
raw_file_path = "rawfile_sample/sensirionsample.csv"

# Absolute paths also work:
raw_file_path = r"C:\Users\YourName\Documents\respiratory_data.csv"
```

#### Step 2: Run the Pipeline

```bash
python main.py
```

**Output:**
- `output/auto_breath_table_[filename].csv` - Standard CSV format
- `output/vt_report_[filename].html` - Interactive HTML report with BPM calculation

### Supported File Formats

The tool automatically detects and processes two main formats:

#### SOTAIRIQ Format
- **File naming**: Usually ends with timestamp like `_250730Z142300T.csv`
- **Structure**: Contains `ts_ms`, `in_flow_vol_ml`, `ex_vol_ml`, etc.
- **Example**: `testAlex_250730Z142300T.csv`

#### Sensirion Format  
- **File naming**: Often includes date/time like `001-1HR-20250125_07h14m51s_AM_-0800_52m26s.csv`
- **Structure**: Contains `Time`, `Flow`, `Pressure`, etc.
- **Example**: `001-1HR-20250125_07h14m51s_AM_-0800_52m26s.csv`

### File Path Configuration Tips

1. **Relative Paths**: Place your data files in the `rawfile_sample/` folder for easy access
2. **Absolute Paths**: Use full paths like `C:\Data\myfile.csv` for files outside the project
3. **Path Separators**: Use forward slashes `/` or raw strings `r"path\to\file.csv"` on Windows
4. **File Validation**: The tool will check if the file exists before processing

### Option 2: QA Backend Only

For just breath analysis and CSV generation:

```bash
cd qa_backend
python main.py
```

**Output:**
- Standard CSV with breath metrics
- Developer CSV with additional technical data

### Option 3: Programmatic Usage

```python
import pandas as pd
from qa_backend.file_io import read_raw_file
from qa_backend.qa_processing import generate_qa_breath_table, check_qa_table
from qa_backend.csv_export import export_standard_csv
from qa_report_tool.analysis import analyze_vt_distribution
from qa_report_tool.report_html import render_html_report
from qa_report_tool.config import DEFAULT_RANGES, DEFAULT_COLUMN

# Read and process data (auto-detects format)
header_df, breath_table_df, real_data_df = read_raw_file("data.csv")
qa_table = generate_qa_breath_table(real_data_df)
qa_table_cleaned = check_qa_table(qa_table)

# Extract total recording time for BPM calculation
total_time_seconds = None
if 'Time' in real_data_df.columns:
    time_data = pd.to_numeric(real_data_df.iloc[2:]['Time'], errors='coerce').dropna()
    if len(time_data) > 0:
        total_time_seconds = time_data.max()

# Export and analyze
export_standard_csv(qa_table_cleaned, "output.csv", "output/")
results = analyze_vt_distribution(
    pd.read_csv("output/output.csv"), 
    column=DEFAULT_COLUMN, 
    ranges=DEFAULT_RANGES,
    total_time_seconds=total_time_seconds
)
render_html_report(results, DEFAULT_RANGES, "session_id", "report.html")
```

## 📊 Output Formats

### Standard CSV Columns
- **Breath Number**: Sequential breath count
- **Peak Pressure**: Maximum pressure during breath (cmH2O)
- **Peak Flow**: Maximum flow rate (L/min)
- **Inhaled Tidal Volume**: Volume of air inhaled (mL)
- **Exhaled Tidal Volume**: Volume of air exhaled (mL)
- **Inspiratory Time**: Duration of inspiration (s)
- **Inspiratory Flow Time**: Duration of inspiratory flow (s)
- **SOTAIR Activation**: SOTAIR flag (0/1)

### HTML Report Features
- **Summary Statistics**: Total breaths, breaths per minute, min/max tidal volumes
- **Distribution Analysis**: Percentage of breaths in configurable ranges (including <400mL and >600mL)
- **Interactive Charts**: Plotly-powered visualizations with bar chart at the top
- **Session Tracking**: Unique session IDs for report management
- **Accurate BPM**: Calculated using total recording time from source data

## ⚙️ Configuration

### Breath Detection Parameters
```python
# In qa_backend/config.py
class BreathDetectionConfig:
    positive_flow_threshold = (1.0, 5.0)  # L/min
    positive_pressure_threshold = 1.0      # cmH2O
    negative_flow_threshold = (1.0, 2.0)   # L/min
    negative_pressure_threshold = 0.1      # cmH2O
```

### SOTAIR Analysis
```python
class SOTAIRConfig:
    gradient_threshold = -1000    # Flow gradient threshold
    time_gap_threshold = 0.25     # Time gap threshold (s)
```

### Report Ranges
```python
# In qa_report_tool/config.py
DEFAULT_RANGES = [(None, 400), (400, 500), (500, 600), (600, None)]  # mL
DEFAULT_COLUMN = "Inhaled Tidal Volume"
```

## 🔧 Advanced Features

### Custom Column Mappings
Create custom CSV exports with specific column names and units:

```python
from qa_backend.csv_export import create_custom_mapping, generate_custom_csv

custom_mapping = create_custom_mapping({
    'breath_number': 'Breath ID',
    'peak_pressure': 'Max Pressure (cmH2O)'
})

generate_custom_csv(qa_table, "custom_output.csv", custom_mapping)
```

### Breath Phase Detection
The system automatically detects:
- **Breath Start/End**: Based on flow and pressure thresholds
- **Inspiration End**: Plateau detection in flow signal
- **Expiration Start**: Negative flow threshold crossing
- **Breath Refinement**: Zero-crossing optimization

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory
2. **File Not Found**: Update file paths in main.py files
3. **No Breaths Detected**: Check if your data meets the detection thresholds
4. **Empty QA Table**: Verify data quality and QA validation parameters

### Debug Mode
Add debug prints in the processing functions to trace data flow:

```python
print(f"Raw data shape: {real_data_df.shape}")
print(f"Breaths detected: {len(qa_table)}")
print(f"Breaths after QA: {len(qa_table_cleaned)}")
```

## 📈 Performance Notes

- **Processing Speed**: ~1000 breaths/second on modern hardware
- **Memory Usage**: ~50MB for typical 1-hour recording
- **File Size**: Standard CSV ~100KB per 1000 breaths

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license information here]

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

---

**Note**: This tool supports both Sensirion and SOTAIRIQ respiratory data formats. The system automatically detects the file format and processes accordingly. Ensure your input data follows one of the supported CSV formats with appropriate time, flow, and pressure columns.