@echo off
REM Run FastAPI backend + Next.js frontend locally
cd /d "%~dp0.."

echo Starting ZM backend + frontend...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo Node/npm not found. Install Node.js from https://nodejs.org
    pause
    exit /b 1
)

python -m pip install -e . -q

if not exist "data\cache\restaurants_v1.jsonl" (
    echo Loading restaurant data...
    python -m zm load-data
)

echo.
echo [1/2] Backend API  -> http://127.0.0.1:8000  (docs: /docs)
echo [2/2] Frontend UI  -> http://localhost:3000
echo.
echo Keep both windows open. Press Ctrl+C in each to stop.
echo.

start "ZM Backend" cmd /k "cd /d %CD% && python -m uvicorn backend.main:create_app --factory --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

cd frontend
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call npm install
)
start "ZM Frontend" cmd /k "cd /d %CD% && npm run dev"

cd ..
echo.
echo Open http://localhost:3000 in your browser.
