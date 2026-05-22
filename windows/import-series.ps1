param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,

    [Parameter(Mandatory = $true)]
    [string]$SeriesTitle,

    [int]$SeasonNumber = 1,
    [string]$SeriesSlug = "",
    [string]$Synopsis = "",
    [string]$PosterUrl = "",
    [ValidateSet("copy", "move")]
    [string]$Mode = "move",
    [switch]$DryRun,
    [string]$EpisodeTitleTemplate = "Серия {episode}",
    [string]$EpisodeDescriptionTemplate = "Серия {episode}"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pythonScript = Join-Path $projectRoot "scripts\import_series.py"

if (-not (Test-Path $pythonScript)) {
    throw "Could not find importer script at $pythonScript"
}

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $pythonExe = "py"
    $pythonPrefix = @("-3")
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Install Python 3 first, or run the import from a machine that already has it."
    }
    $pythonExe = "python"
    $pythonPrefix = @()
}

$arguments = @()
$arguments += $pythonPrefix
$arguments += @(
    $pythonScript,
    "--source-dir", $SourceDir,
    "--series-title", $SeriesTitle,
    "--season-number", $SeasonNumber,
    "--mode", $Mode,
    "--episode-title-template", $EpisodeTitleTemplate,
    "--episode-description-template", $EpisodeDescriptionTemplate
)

if ($SeriesSlug) {
    $arguments += @("--series-slug", $SeriesSlug)
}

if ($Synopsis) {
    $arguments += @("--synopsis", $Synopsis)
}

if ($PosterUrl) {
    $arguments += @("--poster-url", $PosterUrl)
}

if ($DryRun) {
    $arguments += "--dry-run"
}

Write-Host ""
Write-Host "Importing series into Nastenka Flix" -ForegroundColor Cyan
Write-Host "Source: $SourceDir"
Write-Host "Series: $SeriesTitle"
Write-Host "Season: $SeasonNumber"
Write-Host "Mode: $Mode"
Write-Host ""

& $pythonExe $arguments
