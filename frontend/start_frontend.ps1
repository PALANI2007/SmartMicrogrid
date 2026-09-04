# SmartMicrogrid - Start Frontend Dev Server
# Run this script from the frontend directory

$NODE = "C:\Users\palan\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$VITE = "node_modules\vite\bin\vite.js"

if (-not (Test-Path $NODE)) {
    Write-Error "Node.js not found at $NODE"
    exit 1
}

if (-not (Test-Path $VITE)) {
    Write-Error "Vite not found. Run: python ..\install_missing_deps.py"
    exit 1
}

Write-Host "Starting Vite dev server at http://localhost:5173" -ForegroundColor Cyan
Write-Host "API proxied to http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

& $NODE $VITE --host 0.0.0.0 --port 5173
