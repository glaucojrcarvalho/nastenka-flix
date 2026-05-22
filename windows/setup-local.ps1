$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Set-Location $projectRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

if (-not (Test-Path "backend\catalog.json")) {
    Copy-Item "backend\catalog.example.json" "backend\catalog.json"
    Write-Host "Created backend\catalog.json from backend\catalog.example.json"
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Add '127.0.0.1 nastenka-flix' to C:\Windows\System32\drivers\etc\hosts"
Write-Host "2. Run one or more imports with .\windows\import-series.ps1"
Write-Host "3. Start the app with .\windows\run-local.cmd"
Write-Host "4. Install autostart with .\windows\install-autostart.ps1"
Write-Host "5. Open: http://nastenka-flix"
