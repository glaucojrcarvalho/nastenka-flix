param(
    [Parameter(Mandatory = $true)]
    [string]$SeriesSlug,

    [Parameter(Mandatory = $true)]
    [string]$SeriesTitle,

    [string]$SeriesTitleBase64 = "",
    [string]$EpisodeTitleTemplate = "Episode {episode}",
    [string]$EpisodeTitleTemplateBase64 = "",
    [string]$EpisodeDescriptionTemplate = "Episode {episode}",
    [string]$EpisodeDescriptionTemplateBase64 = "",
    [string]$Synopsis = ""
)

$ErrorActionPreference = "Stop"

function Decode-Base64Utf8 {
    param([string]$Value)
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Value))
}

function Resolve-PythonCommand {
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return @{ Executable = "py"; Prefix = @("-3") }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notlike "*WindowsApps*") {
        return @{ Executable = "python"; Prefix = @() }
    }

    $candidates = @(
        Get-ChildItem "$Env:LocalAppData\Programs\Python" -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName "python.exe" }
    ) | Where-Object { $_ -and (Test-Path $_) }

    if ($candidates) {
        return @{ Executable = $candidates[0]; Prefix = @() }
    }

    throw "Python 3 was not found."
}

if ($SeriesTitleBase64) {
    $SeriesTitle = Decode-Base64Utf8 $SeriesTitleBase64
}
if ($EpisodeTitleTemplateBase64) {
    $EpisodeTitleTemplate = Decode-Base64Utf8 $EpisodeTitleTemplateBase64
}
if ($EpisodeDescriptionTemplateBase64) {
    $EpisodeDescriptionTemplate = Decode-Base64Utf8 $EpisodeDescriptionTemplateBase64
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pythonScript = Join-Path $projectRoot "scripts\update_series_metadata.py"
$python = Resolve-PythonCommand

$arguments = @()
$arguments += $python.Prefix
$arguments += @(
    $pythonScript,
    "--series-slug", $SeriesSlug,
    "--series-title", $SeriesTitle,
    "--episode-title-template", $EpisodeTitleTemplate,
    "--episode-description-template", $EpisodeDescriptionTemplate
)

if ($Synopsis) {
    $arguments += @("--synopsis", $Synopsis)
}

& $python.Executable @arguments
