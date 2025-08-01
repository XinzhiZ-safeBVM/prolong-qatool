@echo off
echo Prolong Report Tool - Build Script
echo ====================================
echo.
echo Installing/updating dependencies...
pip install -r requirements.txt
echo.
echo Building executable...
python build_exe.py
echo.
echo Build process completed!
pause