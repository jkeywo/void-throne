@echo off
cd /d "%~dp0"
python launch.py --multiplayer --port 8878
if errorlevel 1 pause
