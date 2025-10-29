@echo off
REM --- Start backend ---
cd "C:\Data Quality Dashboard\backend"
set FLASK_HOST=127.0.0.1
set FLASK_PORT=5001
set FLASK_DEBUG=1
start cmd /k "python app.py"

REM --- Wait a few seconds to ensure backend is up ---
timeout /t 5

REM --- Start frontend (Windusrf) ---
cd "C:\Data Quality Dashboard\frontend"
start cmd /k "streamlit run app.py"
