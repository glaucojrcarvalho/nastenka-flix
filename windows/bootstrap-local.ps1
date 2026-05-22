$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

function Decode-Base64Utf8 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Value))
}

# Edit this list once on her laptop, then run .\windows\bootstrap-local.cmd
$seriesImports = @(
    @{
        SourceDir = "C:\Users\anast\OneDrive\Desktop\Ne.rodis.krasivoy.200.seriy.iz.200.2005-2006.DivX.DVDRip"
        SeriesTitleBase64 = "0J3QtSDRgNC+0LTQuNGB0Ywg0LrRgNCw0YHQuNCy0L7QuQ=="
        SeriesSlug = "ne-rodis-krasivoy"
        SeasonNumber = 1
        EpisodeTitleTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        EpisodeDescriptionTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        Mode = "move"
    }
    @{
        SourceDirBase64 = "QzpcVXNlcnNcYW5hc3RcT25lRHJpdmVcRGVza3RvcFzQnNC+0Y8g0L/RgNC10LrRgNCw0YHQvdCw0Y8g0L3Rj9C90Y8gRFZEUmlw"
        SeriesTitleBase64 = "0JzQvtGPINC/0YDQtdC60YDQsNGB0L3QsNGPINC90Y/QvdGP"
        SeriesSlug = "moya-prekrasnaya-nyanya"
        SeasonNumber = 1
        EpisodeTitleTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        EpisodeDescriptionTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        Mode = "move"
    }
)

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Ensure-HostsEntry {
    $hostsPath = "$Env:WinDir\System32\drivers\etc\hosts"
    $entry = "127.0.0.1 nastenka-flix"

    if (-not (Test-IsAdmin)) {
        Write-Warning "Run this script as Administrator once if you want it to update the hosts file automatically."
        return
    }

    if (-not (Select-String -Path $hostsPath -Pattern "^\s*127\.0\.0\.1\s+nastenka-flix\s*$" -Quiet -ErrorAction SilentlyContinue)) {
        Add-Content -Path $hostsPath -Value "`r`n$entry"
        ipconfig /flushdns | Out-Null
        Write-Host "Added hosts entry for nastenka-flix." -ForegroundColor Green
    }
}

& ".\windows\setup-local.ps1"
Ensure-HostsEntry

foreach ($series in $seriesImports) {
    $sourceDir = if ($series.ContainsKey("SourceDirBase64") -and $series.SourceDirBase64) {
        Decode-Base64Utf8 -Value $series.SourceDirBase64
    } else {
        $series.SourceDir
    }

    if (-not $sourceDir) {
        continue
    }

    if (-not (Test-Path $sourceDir)) {
        throw "Source folder not found: $sourceDir"
    }

    $importParams = @{
        SourceDir = $sourceDir
        SeriesSlug = $series.SeriesSlug
        SeasonNumber = [int]$series.SeasonNumber
        Mode = $series.Mode
    }

    if ($series.ContainsKey("SeriesTitleBase64") -and $series.SeriesTitleBase64) {
        $importParams.SeriesTitleBase64 = $series.SeriesTitleBase64
        $importParams.SeriesTitle = "placeholder"
    } else {
        $importParams.SeriesTitle = $series.SeriesTitle
    }

    if ($series.ContainsKey("EpisodeTitleTemplateBase64") -and $series.EpisodeTitleTemplateBase64) {
        $importParams.EpisodeTitleTemplateBase64 = $series.EpisodeTitleTemplateBase64
    } else {
        $importParams.EpisodeTitleTemplate = $series.EpisodeTitleTemplate
    }

    if ($series.ContainsKey("EpisodeDescriptionTemplateBase64") -and $series.EpisodeDescriptionTemplateBase64) {
        $importParams.EpisodeDescriptionTemplateBase64 = $series.EpisodeDescriptionTemplateBase64
    } else {
        $importParams.EpisodeDescriptionTemplate = $series.EpisodeDescriptionTemplate
    }

    if ($series.ContainsKey("Synopsis") -and $series.Synopsis) {
        $importParams.Synopsis = $series.Synopsis
    }

    if ($series.ContainsKey("PosterUrl") -and $series.PosterUrl) {
        $importParams.PosterUrl = $series.PosterUrl
    }

    & ".\windows\import-series.ps1" @importParams
}

& ".\windows\run-local.ps1" -Build
& ".\windows\install-autostart.ps1"

Write-Host ""
Write-Host "Everything is ready." -ForegroundColor Green
Write-Host "Open http://nastenka-flix"
