param(
    [string]$TaskName = "Nastenka Flix"
)

$ErrorActionPreference = "Stop"

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Removed autostart task: $TaskName" -ForegroundColor Green
