# Restructured Respiratory Data Analysis Tool

This is a restructured and improved version of the respiratory data analysis tool, organized into modular, maintainable Python code following best practices.

## 📁 Project Structure

```
restructured/
├── __init__.py              # Package initialization
├── main.py                  # Main script and example usage
├── config.py                # Configuration settings and parameters
├── file_io.py               # File reading and data parsing
├── breath_detection.py      # Breath detection algorithms
├── calculations.py          # Mathematical calculations
├── qa_processing.py         # QA table generation and validation
├── csv_export.py           # CSV export functionality
└── README.md               # This documentation
```

## 🚀 Quick Start

### Basic Usage

```python
from file_io import read_sensirion_file
from qa_processing import generate_qa_breath_table, check_qa_table
from csv_export import export_standard_csv

# Read data
header_df, breath_table_df, real_data_df = read_sensirion_file("your_file.csv")

# Generate QA table
qa_table = generate_qa_breath_table(real_data_df)
qa_table_clean = check_qa_table(qa_table)

# Export results
export_standard_csv(qa_table_clean, "output.csv", "output_dir/")
```

### Running the Main Script

```bash
python main.py
```

*Note: Update the `raw_file_path` variable in `main.py` with your actual data file path.*

## 📋 Module Documentation

### 1. `file_io.py` - File Input/Output

**Main Functions:**
- `read_sensirion_file(filepath)` - Reads Sensirion CSV files and returns header, breath table, and real data DataFrames

**Features:**
- Automatic file format detection
- Data type conversion
- TSI device detection and warnings
- Error handling for file operations

### 2. `breath_detection.py` - Breath Detection Algorithms

**Main Functions:**
- `detect_breaths(df)` - Primary breath detection using flow and pressure thresholds
- `detect_breath_phases(df, starts, ends)` - Detects inspiration end and expiration start
- `refine_breath_detection(df, starts, ends)` - Refines breath boundaries using zero-crossing

**Features:**
- Configurable thresholds
- Multi-stage detection pipeline
- Robust error handling
- Plateau detection for inspiration phases

### 3. `calculations.py` - Mathematical Operations

**Main Functions:**
- `calculate_volume(time_data, flow_data, start, end)` - Volume integration using trapezoidal rule
- `find_max_in_slice(data, start, end)` - Find maximum value in data slice
- `calc_mean_in_slice(data, start, end)` - Calculate mean value in data slice
- `analyze_sotair_single_breath(...)` - SOTAIR analysis for individual breaths

**Features:**
- Numerical integration for volume calculation
- Statistical analysis functions
- SOTAIR (Sustained Opening of The Airway) detection
- Input validation and error handling

### 4. `qa_processing.py` - QA Table Generation

**Main Functions:**
- `generate_qa_breath_table(real_data_df)` - Complete QA table generation pipeline
- `check_qa_table(qa_table)` - Validation and cleaning of QA results
- `refine_qa_breath_table(real_data_df, user_table)` - User-guided refinement

**Features:**
- End-to-end breath analysis pipeline
- Configurable validation thresholds
- Automatic outlier detection and removal
- Comprehensive breath metrics calculation

### 5. `csv_export.py` - Data Export

**Main Functions:**
- `export_standard_csv(qa_table, filename, output_dir)` - Standard format export
- `export_developer_csv(qa_table, filename, output_dir)` - Extended format export
- `generate_custom_csv(qa_table, filename, mapping, output_dir)` - Custom format export

**Features:**
- Multiple export formats (standard/developer)
- Customizable column mapping
- Unit specification in output
- Automatic directory creation

### 6. `config.py` - Configuration Management

**Configuration Classes:**
- `BreathDetectionConfig` - Breath detection parameters
- `SOTAIRConfig` - SOTAIR analysis settings
- `QAValidationConfig` - Quality assurance thresholds
- `FileIOConfig` - File handling settings
- `ExportConfig` - Export format settings

**Features:**
- Centralized parameter management
- Easy configuration updates
- Type hints and documentation
- Default value management

## ⚙️ Configuration

### Customizing Detection Parameters

```python
from config import get_breath_detection_config

config = get_breath_detection_config()
config.POSITIVE_FLOW_THRESHOLD = (1.5, 6.0)  # Adjust thresholds
config.INSP_END_SKIP = 25  # Adjust phase detection
```

### Custom Export Mapping

```python
from csv_export import create_custom_mapping, generate_custom_csv

custom_mapping = create_custom_mapping({
    'breath_number': {'new_name': 'Breath ID', 'unit': 'count'},
    'peak_pressure': {'new_name': 'Max Pressure', 'unit': 'cmH2O'},
    'inspiratory_volume': {'new_name': 'Tidal Volume', 'unit': 'mL'}
})

generate_custom_csv(qa_table, "custom_output.csv", custom_mapping)
```

## 🔧 Key Improvements Over Original Code

### 1. **Modular Architecture**
- Separated concerns into logical modules
- Clear interfaces between components
- Easier testing and maintenance

### 2. **Better Error Handling**
- Comprehensive exception handling
- Informative error messages
- Graceful failure modes

### 3. **Configuration Management**
- Centralized parameter configuration
- Easy customization without code changes
- Type safety and validation

### 4. **Code Quality**
- Consistent naming conventions (snake_case)
- Comprehensive docstrings
- Type hints throughout
- PEP 8 compliance

### 5. **Functionality**
- Removed duplicate imports
- Eliminated hardcoded paths
- Added input validation
- Improved algorithm robustness

### 6. **Usability**
- Clear API design
- Example usage patterns
- Comprehensive documentation
- Flexible export options

## 📊 Output Formats

### Standard CSV Output
Includes essential breath metrics:
- Breath Number
- Peak Pressure (cmH2O)
- Peak Flow (L/min)
- Inhaled/Exhaled Tidal Volume (mL)
- Inspiratory Time (s)
- SOTAIR Activation (boolean)

### Developer CSV Output
Includes all available metrics:
- All standard metrics plus:
- Mean Pressure During Inspiration
- Detailed timing information
- Breath timestamps
- Additional diagnostic data

## 🐛 Troubleshooting

### Common Issues

1. **File Not Found Error**
   - Check file path is correct
   - Ensure file exists and is accessible
   - Use raw strings for Windows paths: `r"C:\path\to\file.csv"`

2. **No Breaths Detected**
   - Check data quality and format
   - Adjust detection thresholds in config
   - Verify flow and pressure data are present

3. **Import Errors**
   - Ensure all modules are in the same directory
   - Check Python path configuration
   - Verify all dependencies are installed

### Getting Help

For issues or questions:
1. Check the error messages for specific guidance
2. Review the configuration parameters
3. Examine the input data format
4. Consult the module docstrings for detailed API information

## 📈 Performance Notes

- The restructured code maintains the same algorithmic complexity as the original
- Memory usage is optimized through better data handling
- Processing time may be slightly improved due to reduced redundancy
- Large files (>100MB) should be processed with adequate system memory

## 🔄 Migration from Original Code

To migrate from the original `old_backend/main.py`:

1. Replace direct function calls with module imports
2. Update file paths to use the new API
3. Adjust any custom thresholds using the config system
4. Update output handling to use the new export functions

Example migration:

```python
# Old code
header_PD, breath_table_PD, real_data_PD = ReadSensirionFile(filepath)
QA_table = generate_qa_breath_table(real_data_PD)

# New code
from file_io import read_sensirion_file
from qa_processing import generate_qa_breath_table

header_df, breath_table_df, real_data_df = read_sensirion_file(filepath)
qa_table = generate_qa_breath_table(real_data_df)
```