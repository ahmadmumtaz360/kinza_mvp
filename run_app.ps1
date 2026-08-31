$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Project virtual environment not found. Run: python -m venv .venv"
}

& $venvPython -c "from databricks import sql; import streamlit"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing missing project dependencies..." -ForegroundColor Yellow
    & $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
}

Write-Host "Starting Kinza with the project virtual environment..." -ForegroundColor Green
Write-Host "Open http://localhost:8502" -ForegroundColor Cyan
& $venvPython -m streamlit run (Join-Path $projectRoot "app.py") --server.port 8502

