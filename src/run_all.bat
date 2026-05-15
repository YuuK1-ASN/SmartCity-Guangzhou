@echo off
cd /d %~dp0\..
if not exist .venv (
  py -3.13 -m venv .venv
)
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\fetch_aqicn_all_stations_bbox.py
.\.venv\Scripts\python.exe src\fetch_gz_metro_lines_from_osm.py
.\.venv\Scripts\python.exe -m streamlit run webapp\app_main.py
pause
