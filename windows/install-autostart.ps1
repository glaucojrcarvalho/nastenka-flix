param(
    [string]$TaskName = "Nastenka Flix",
    [switch]$BuildOnStart
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$runScript = Join-Path $scriptDir "run-local.ps1"

if (-not (Test-Path $runScript)) {
    throw "Could not find run-local.ps1 at $runScript"
}

$argumentList = "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`""
if ($BuildOnStart) {
    $argumentList += " -Build"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argumentList -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $Env:USERNAME
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Starts Nastenka Flix when $Env:USERNAME signs in." `
    -Force | Out-Null

Write-Host "Installed autostart task: $TaskName" -ForegroundColor Green
Write-Host "Nastenka Flix will start automatically when $Env:USERNAME signs in."
