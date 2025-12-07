@echo off
cd /d "%~dp0"
python run.py >nul 2>&1
exit /b
