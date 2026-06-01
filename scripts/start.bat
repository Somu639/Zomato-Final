@echo off
REM Start ZM Streamlit app (Windows). Opens http://127.0.0.1:8501
cd /d "%~dp0.."
echo.
echo ZM Restaurant Recommendations
echo ==============================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not on PATH.
    echo Install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -e . -q
if errorlevel 1 (
    echo pip install failed.
    pause
    exit /b 1
)

if not exist "data\cache\restaurants_v1.jsonl" (
    echo.
    echo First run: downloading restaurant data (may take a few minutes)...
    python -m zm load-data
)

echo.
echo Starting app at http://127.0.0.1:8501/
echo Do NOT use port 8000 — Streamlit runs on 8501.
echo Keep this window open while using the app.
echo.
python -m zm streamlit
