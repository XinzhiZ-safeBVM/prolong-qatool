# Prolong Report Tool - Complete Setup & Build Guide

A comprehensive step-by-step guide for setting up the development environment and building the executable on Windows.

## 📋 Prerequisites

- **Windows 10/11** (64-bit recommended)
- **Anaconda or Miniconda** installed
- **Python 3.12** (will be installed via conda)
- **Git** installed (for version tracking)
- **Internet connection** (for downloading dependencies)

## 🚀 Step-by-Step Setup

### Step 1: Create Conda Environment

1. **Open Anaconda Prompt** (or Command Prompt/PowerShell if conda is in PATH)

2. **Create a new environment** with Python 3.12:
   ```bash
   conda create -n prolong-report-tool python=3.12
   ```

3. **Activate the environment**:
   ```bash
   conda activate prolong-report-tool
   ```

### Step 2: Clone/Download Project

1. **Navigate to your desired directory**:
   ```bash
   cd C:\Users\YourName\Documents
   ```

2. **Clone the repository** (if using Git):
   ```bash
   git clone <repository-url>
   cd prolong-qatool
   ```
   
   **OR download and extract** the project folder if not using Git.

### Step 3: Install Dependencies

1. **Ensure you're in the project directory**:
   ```bash
   cd prolong-qatool
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `pandas>=2.3.1` - Data processing
   - `numpy>=2.3.0` - Numerical computations
   - `pyinstaller>=6.14.2` - Executable building

### Step 4: Test the Application

1. **Test the GUI application**:
   ```bash
   python gui_main.py
   ```

2. **Verify functionality**:
   - GUI should open with "Prolong Report Tool" title
   - Version should display (git hash or "Unknown")
   - Browse button should work
   - Try processing a sample CSV file from `rawfile_sample/`

3. **Close the application** when testing is complete.

### Step 5: Build the Executable

#### Option A: Quick Build (Recommended)

1. **Run the batch file**:
   ```bash
   build.bat
   ```
   
   This will:
   - Install/update dependencies
   - Create version.txt with git hash
   - Build the executable
   - Show completion status

#### Option B: Manual Build

1. **Run the Python build script**:
   ```bash
   python build_exe.py
   ```

2. **Wait for completion** (may take 2-5 minutes)

### Step 6: Locate and Test Executable

1. **Find the executable**:
   ```
   dist/ProlongReportTool.exe
   ```

2. **Test the executable**:
   - Double-click `ProlongReportTool.exe`
   - Verify it opens without errors
   - Test with a sample CSV file
   - Confirm HTML report generation and opening

## 📁 Project Structure After Build

```
prolong-qatool/
├── dist/
│   └── ProlongReportTool.exe    # ← Your executable!
├── build/                       # Build artifacts (can delete)
├── ProlongReportTool.spec      # PyInstaller spec (can delete)
├── version.txt                 # Git hash file (auto-generated)
└── ... (source files)
```

## 🎯 Distribution

### For End Users:

1. **Copy the executable**:
   - Take `dist/ProlongReportTool.exe`
   - This is the only file users need!

2. **No installation required**:
   - Users can run it directly
   - No Python or dependencies needed
   - Self-contained application

### System Requirements for End Users:
- Windows 10/11
- 4GB RAM minimum
- 100MB free disk space

## 🔧 Troubleshooting

### Common Issues:

#### "conda not recognized"
- **Solution**: Install Anaconda/Miniconda or add conda to PATH
- **Alternative**: Use regular Python with `pip install -r requirements.txt`

#### "git not recognized" during build
- **Impact**: Version will show "Unknown" (functionality not affected)
- **Solution**: Install Git or ignore if version tracking not needed

#### Build fails with "Module not found"
- **Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`
- **Check**: Conda environment is activated

#### Executable won't start
- **Check**: Windows Defender/antivirus not blocking
- **Solution**: Add exception for the executable
- **Alternative**: Run from command line to see error messages

#### Large executable size (50-100MB)
- **Normal**: PyInstaller bundles entire Python runtime
- **Not an issue**: Modern systems handle this easily

### Build Optimization:

#### Reduce executable size:
```bash
# Edit build_exe.py and add:
'--exclude-module', 'matplotlib',
'--exclude-module', 'scipy',
# (for any unused large packages)
```

#### Add custom icon:
1. Place `icon.ico` in project root
2. Build script will automatically include it

## 🔄 Development Workflow

### For ongoing development:

1. **Activate environment**:
   ```bash
   conda activate prolong-report-tool
   ```

2. **Make changes** to source code

3. **Test changes**:
   ```bash
   python gui_main.py
   ```

4. **Rebuild when ready**:
   ```bash
   build.bat
   ```

### Version Management:
- Each build captures current git commit hash
- Displayed in GUI for version tracking
- Helps identify which version users are running

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify all prerequisites are installed
3. Test in a fresh conda environment
4. Check Windows Event Viewer for detailed error messages

---

**Success!** You now have a fully functional Prolong Report Tool executable ready for distribution! 🎉