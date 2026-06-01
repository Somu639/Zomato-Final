# Start ZM Streamlit app (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host ""
Write-Host "ZM Restaurant Recommendations" -ForegroundColor Red
Write-Host "==============================" -ForegroundColor Red
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or not on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from https://python.org"
    exit 1
}

Write-Host "Installing dependencies..."
python -m pip install -e . -q

$cache = "data\cache\restaurants_v1.jsonl"
if (-not (Test-Path $cache)) {
    Write-Host ""
    Write-Host "First run: downloading restaurant data (may take a few minutes)..."
    python -m zm load-data
}

Write-Host ""
Write-Host "Starting app at http://127.0.0.1:8501/" -ForegroundColor Green
Write-Host "Do NOT use port 8000 — Streamlit runs on 8501."
Write-Host "Keep this terminal open while using the app."
Write-Host ""
python -m zm streamlit
