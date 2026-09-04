# SmartMicrogrid - Start Backend Server
# Run this script from the backend directory

Write-Host "Starting FastAPI backend at http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs at http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
