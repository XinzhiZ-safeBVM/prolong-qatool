#!/usr/bin/env python3
"""
Build script for creating Prolong Report Tool executable using PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def create_version_file():
    """Create version.txt file with current git hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            git_hash = result.stdout.strip()
            with open('version.txt', 'w') as f:
                f.write(git_hash)
            print(f"Created version.txt with git hash: {git_hash[:8]}...")
            return True
    except Exception as e:
        print(f"Warning: Could not create version.txt: {e}")
    return False

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Create version file
    create_version_file()
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--windowed',  # Hide console window (for GUI apps)
        '--name', 'ProlongReportTool',  # Name of the executable
        '--icon', 'icon.ico',  # Icon file (if you have one)
        '--add-data', 'qa_backend;qa_backend',  # Include qa_backend package
        '--add-data', 'qa_report_tool;qa_report_tool',  # Include qa_report_tool package
        '--add-data', 'version.txt;.',  # Include version file
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'plotly',
        '--hidden-import', 'jinja2',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'webbrowser',
        '--hidden-import', 'subprocess',
        'gui_main.py'  # Main script
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not (current_dir / 'icon.ico').exists():
        cmd = [arg for arg in cmd if arg != '--icon' and arg != 'icon.ico']
    
    # Remove version.txt parameter if it doesn't exist
    if not (current_dir / 'version.txt').exists():
        cmd = [arg for arg in cmd if not arg.startswith('version.txt')]
    
    print("Building executable with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, cwd=current_dir, check=True)
        
        print("\n✓ Executable built successfully!")
        print(f"Executable location: {current_dir / 'dist' / 'ProlongReportTool.exe'}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def main():
    """Main function"""
    print("Prolong Report Tool - Executable Builder")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('gui_main.py').exists():
        print("Error: gui_main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Build the executable
    success = build_executable()
    
    if success:
        print("\nBuild completed successfully!")
        print("\nTo distribute the application:")
        print("1. Copy the executable from the 'dist' folder")
        print("2. The executable is self-contained and doesn't require Python installation")
        print("3. Users can run it directly by double-clicking")
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()