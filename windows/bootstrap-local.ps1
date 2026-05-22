$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

# Edit this list once on her laptop, then run .\windows\bootstrap-local.cmd
$seriesImports = @(
    @{
        SourceDir = "C:\Users\anast\OneDrive\Desktop\Ne.rodis.krasivoy.200.seriy.iz.200.2005-2006.DivX.DVDRip"
        SeriesTitle = "Не родись красивой"
        SeriesSlug = "ne-rodis-krasivoy"
        SeasonNumber = 1
        EpisodeTitleTemplate = "Серия {episode}"
        EpisodeDescriptionTemplate = "Серия {episode}"
        Mode = "move"
    }
    @{
        SourceDir = "C:\Users\anast\OneDrive\Desktop\Моя прекрасная няня DVDRip"
        SeriesTitle = "Моя прекрасная няня"
        SeriesSlug = "moya-prekrasnaya-nyanya"
        SeasonNumber = 1
        EpisodeTitleTemplate = "Серия {episode}"
        EpisodeDescriptionTemplate = "Серия {episode}"
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
    if (-not $series.SourceDir) {
        continue
    }

    if (-not (Test-Path $series.SourceDir)) {
        throw "Source folder not found: $($series.SourceDir)"
    }

    $arguments = @(
        "-SourceDir", $series.SourceDir,
        "-SeriesTitle", $series.SeriesTitle,
        "-SeriesSlug", $series.SeriesSlug,
        "-SeasonNumber", [string]$series.SeasonNumber,
        "-EpisodeTitleTemplate", $series.EpisodeTitleTemplate,
        "-EpisodeDescriptionTemplate", $series.EpisodeDescriptionTemplate,
        "-Mode", $series.Mode
    )

    if ($series.ContainsKey("Synopsis") -and $series.Synopsis) {
        $arguments += @("-Synopsis", $series.Synopsis)
    }

    if ($series.ContainsKey("PosterUrl") -and $series.PosterUrl) {
        $arguments += @("-PosterUrl", $series.PosterUrl)
    }

    & ".\windows\import-series.ps1" @arguments
}

& ".\windows\run-local.ps1" -Build
& ".\windows\install-autostart.ps1"

Write-Host ""
Write-Host "Everything is ready." -ForegroundColor Green
Write-Host "Open http://nastenka-flix"
