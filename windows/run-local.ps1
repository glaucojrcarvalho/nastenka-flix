param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"

function Test-DockerEngine {
    try {
        docker info *> $null
        return $true
    } catch {
        return $false
    }
}

function Start-DockerDesktop {
    $candidates = @(
        "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$Env:ProgramFiles(x86)\Docker\Docker\Docker Desktop.exe",
        "$Env:LocalAppData\Programs\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { $_ -and (Test-Path $_) }

    if (-not $candidates) {
        throw "Docker Desktop.exe was not found. Install Docker Desktop first."
    }

    $isDockerDesktopRunning = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if (-not $isDockerDesktopRunning) {
        Start-Process -FilePath $candidates[0] | Out-Null
    }
}

function Wait-ForDockerEngine {
    param(
        [int]$TimeoutSeconds = 240
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-DockerEngine) {
            return
        }
        Start-Sleep -Seconds 3
    }

    throw "Docker engine did not become ready within $TimeoutSeconds seconds."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI was not found. Install Docker Desktop first."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

if (-not (Test-Path "backend\catalog.json")) {
    Copy-Item "backend\catalog.example.json" "backend\catalog.json"
    Write-Host "Created backend\catalog.json from backend\catalog.example.json"
}

if (-not (Test-DockerEngine)) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
    Start-DockerDesktop
    Write-Host "Waiting for Docker engine..." -ForegroundColor Cyan
    Wait-ForDockerEngine
}

$composeArgs = @("compose", "up", "-d")
if ($Build) {
    $composeArgs += "--build"
}

Write-Host "Starting Nastenka Flix..." -ForegroundColor Cyan
& docker $composeArgs

Write-Host ""
Write-Host "Nastenka Flix is available at http://nastenka-flix" -ForegroundColor Green
