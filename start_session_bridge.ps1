Write-Host "Starting CATDAMS Session Bridge..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the bridge" -ForegroundColor Yellow
Write-Host ""
try {
    python session_bridge.py
} catch {
    Write-Host "Error starting session bridge: $_" -ForegroundColor Red
}
Write-Host "Session bridge stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit" 