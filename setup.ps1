# Enhanced Weather Monitor Setup Script
# Run this in PowerShell to install dependencies

Write-Host "Setting up Enhanced Weather Monitor..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies. Please check your pip installation." -ForegroundColor Red
    exit 1
}

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "`nUsage examples:" -ForegroundColor Cyan
Write-Host "  python weather_monitor_enhanced.py KCOHOTSU8" -ForegroundColor White
Write-Host "  python weather_monitor_enhanced.py KCOHOTSU8 --interval 30" -ForegroundColor White
Write-Host "`nFeatures:" -ForegroundColor Cyan
Write-Host "  • htop-like interface with live updates" -ForegroundColor White
Write-Host "  • Color-coded values based on weather ranges" -ForegroundColor White
Write-Host "  • Real-time sparkline graphs" -ForegroundColor White
Write-Host "  • 60-second refresh (customizable)" -ForegroundColor White
Write-Host "  • Fallback display if rich library unavailable" -ForegroundColor White
