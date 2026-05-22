param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,

    [Parameter(Mandatory = $true)]
    [string]$SeriesTitle,

    [string]$SourceDirBase64 = "",
    [string]$SeriesTitleBase64 = "",

    [int]$SeasonNumber = 1,
    [string]$SeriesSlug = "",
    [string]$Synopsis = "",
    [string]$PosterUrl = "",
    [ValidateSet("copy", "move")]
    [string]$Mode = "move",
    [switch]$DryRun,
    [string]$EpisodeTitleTemplate = "Episode {episode}",
    [string]$EpisodeDescriptionTemplate = "Episode {episode}",
    [string]$EpisodeTitleTemplateBase64 = "",
    [string]$EpisodeDescriptionTemplateBase64 = ""
)

$ErrorActionPreference = "Stop"

function Decode-Base64Utf8 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Value))
}

function Resolve-PythonCommand {
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return @{
            Executable = "py"
            Prefix = @("-3")
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notlike "*WindowsApps*") {
        return @{
            Executable = "python"
            Prefix = @()
        }
    }

    $candidates = @(
        Get-ChildItem "$Env:LocalAppData\Programs\Python" -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName "python.exe" },
        Get-ChildItem "$Env:ProgramFiles" -Directory -Filter "Python*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName "python.exe" }
    ) | Where-Object { $_ -and (Test-Path $_) }

    if ($candidates) {
        return @{
            Executable = $candidates[0]
            Prefix = @()
        }
    }

    throw "Python 3 was not found. Install Python 3 first."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pythonScript = Join-Path $projectRoot "scripts\import_series.py"

if (-not (Test-Path $pythonScript)) {
    throw "Could not find importer script at $pythonScript"
}

$pythonCommand = Resolve-PythonCommand
$pythonExe = $pythonCommand.Executable
$pythonPrefix = $pythonCommand.Prefix

if ($SourceDirBase64) {
    $SourceDir = Decode-Base64Utf8 -Value $SourceDirBase64
}

if ($SeriesTitleBase64) {
    $SeriesTitle = Decode-Base64Utf8 -Value $SeriesTitleBase64
}

if ($EpisodeTitleTemplateBase64) {
    $EpisodeTitleTemplate = Decode-Base64Utf8 -Value $EpisodeTitleTemplateBase64
}

if ($EpisodeDescriptionTemplateBase64) {
    $EpisodeDescriptionTemplate = Decode-Base64Utf8 -Value $EpisodeDescriptionTemplateBase64
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
Write-Host "Python: $pythonExe"
Write-Host ""

& $pythonExe @arguments
