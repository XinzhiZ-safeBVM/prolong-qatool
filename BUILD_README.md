# Building Prolong Report Tool Executable

This guide explains how to create a standalone executable (.exe) file for the Prolong Report Tool using PyInstaller.

## Quick Start

### Option 1: Using the Build Script (Recommended)

1. **Run the batch file** (Windows):
   ```bash
   build.bat
   ```
   This will automatically install dependencies and build the executable.

2. **Or run the Python build script**:
   ```bash
   python build_exe.py
   ```

### Option 2: Manual PyInstaller Command

```bash
pyinstaller --onefile --windowed --name ProlongReportTool --add-data "qa_backend;qa_backend" --add-data "qa_report_tool;qa_report_tool" gui_main.py
```

## Prerequisites

1. **Python 3.7+** installed
2. **All project dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```
3. **PyInstaller** installed:
   ```bash
   pip install pyinstaller
   ```

## Build Process

The build process will:

1. **Install Dependencies**: Ensure all required packages are available
2. **Bundle Application**: Package the GUI application with all dependencies
3. **Include Modules**: Add qa_backend and qa_report_tool packages
4. **Create Executable**: Generate a single .exe file in the `dist` folder
5. **Version Tracking**: Include git hash functionality for version identification

## Output

After successful build:
- **Executable**: `dist/ProlongReportTool.exe`
- **Build files**: `build/` folder (can be deleted)
- **Spec file**: `ProlongReportTool.spec` (PyInstaller configuration)

## Features in Executable

✅ **Complete GUI Interface**
- File picker for CSV selection
- Real-time processing output
- Automatic HTML report opening

✅ **Version Tracking**
- Displays git commit hash in the interface
- Helps track which version is being used

✅ **Smart Output Location**
- Creates `html_report` folder next to selected CSV file
- No need to navigate to find output files

✅ **Self-Contained**
- No Python installation required on target machines
- All dependencies bundled
- Single executable file

## Distribution

### For End Users:
1. Copy `ProlongReportTool.exe` from the `dist` folder
2. No additional installation required
3. Double-click to run the application
4. Select CSV file and click "Run Analysis"

### System Requirements:
- Windows 10/11 (64-bit recommended)
- Minimum 4GB RAM
- 100MB free disk space

## Troubleshooting

### Common Issues:

1. **"Module not found" errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Add missing modules to the `--hidden-import` list in build script

2. **"Git not found" errors**:
   - Install Git or the executable will show "Unknown" for version
   - This doesn't affect core functionality

3. **Large executable size**:
   - Normal for bundled applications (typically 50-100MB)
   - PyInstaller includes entire Python runtime

4. **Antivirus false positives**:
   - Some antivirus software may flag PyInstaller executables
   - Add exception or use code signing certificate

### Build Optimization:

- **Reduce size**: Use `--exclude-module` for unused packages
- **Add icon**: Place `icon.ico` in project root before building
- **Code signing**: Use certificate for trusted distribution

## Version Management

The application uses a dual approach for version tracking:

### Development Environment:
- **Git command**: Directly queries `git rev-parse HEAD` for current commit hash
- **Real-time**: Always shows the latest commit hash
- **Requires**: Git installation and .git directory

### Executable Environment:
- **Version file**: Reads from bundled `version.txt` file
- **Build-time capture**: Git hash is captured during build process
- **Self-contained**: No external dependencies required

### How it Works:
1. **Build Process**: `build_exe.py` runs `git rev-parse HEAD` and saves result to `version.txt`
2. **PyInstaller**: Bundles `version.txt` with the executable using `--add-data`
3. **Runtime**: GUI first checks for `version.txt`, falls back to git command
4. **Display**: Shows first 8 characters of commit hash in the interface

This ensures version tracking works in both development and distributed executable environments.

## Advanced Configuration

Edit `build_exe.py` to customize:
- Executable name and icon
- Additional data files
- Hidden imports
- Build options

For more PyInstaller options, see: https://pyinstaller.readthedocs.io/