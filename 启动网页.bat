@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3.13 -m venv .venv
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" -m streamlit run webapp\app_main.py

pause
