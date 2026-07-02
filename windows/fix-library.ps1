param(
    [switch]$DeleteOriginalAvi,
    [switch]$MetadataOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

function Decode-Base64Utf8 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Value))
}

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

function Ensure-DockerEngine {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker CLI was not found. Install Docker Desktop first."
    }

    if (-not (Test-DockerEngine)) {
        Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
        Start-DockerDesktop
        Write-Host "Waiting for Docker engine..." -ForegroundColor Cyan
        Wait-ForDockerEngine
    }
}

function To-WorkspacePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AbsolutePath
    )

    $resolvedProjectRoot = [System.IO.Path]::GetFullPath($projectRoot)
    $resolvedAbsolutePath = [System.IO.Path]::GetFullPath($AbsolutePath)

    if (-not $resolvedAbsolutePath.StartsWith($resolvedProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the project root: $AbsolutePath"
    }

    $relativePath = $resolvedAbsolutePath.Substring($resolvedProjectRoot.Length).TrimStart("\")
    return ("/workspace/" + ($relativePath -replace "\\", "/"))
}

function Convert-AviToMp4 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InputPath,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $inputWorkspacePath = To-WorkspacePath -AbsolutePath $InputPath
    $outputWorkspacePath = To-WorkspacePath -AbsolutePath $OutputPath

    $arguments = @(
        "run",
        "--rm",
        "-v", "${projectRoot}:/workspace",
        "-w", "/workspace",
        "jrottenberg/ffmpeg:6.0-ubuntu",
        "-y",
        "-i", $inputWorkspacePath,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        $outputWorkspacePath
    )

    & docker @arguments
}

function Get-VideoDurationSeconds {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VideoPath
    )

    $workspaceVideoPath = To-WorkspacePath -AbsolutePath $VideoPath
    $arguments = @(
        "run",
        "--rm",
        "-v", "${projectRoot}:/workspace",
        "-w", "/workspace",
        "jrottenberg/ffmpeg:6.0-ubuntu",
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        $workspaceVideoPath
    )

    $durationOutput = (& docker @arguments | Out-String).Trim()
    if (-not $durationOutput) {
        return 0
    }

    return [int][math]::Floor([double]$durationOutput)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

$catalogPath = Join-Path $projectRoot "backend\catalog.json"
$mediaRoot = Join-Path $projectRoot "media\series"

$seriesMetadata = @{
    "ne-rodis-krasivoy" = @{
        TitleBase64 = "0J3QtSDRgNC+0LTQuNGB0Ywg0LrRgNCw0YHQuNCy0L7QuQ=="
        EpisodeTitleTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        EpisodeDescriptionTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
    }
    "moya-prekrasnaya-nyanya" = @{
        TitleBase64 = "0JzQvtGPINC/0YDQtdC60YDQsNGB0L3QsNGPINC90Y/QvdGP"
        EpisodeTitleTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
        EpisodeDescriptionTemplateBase64 = "0KHQtdGA0LjRjyB7ZXBpc29kZX0="
    }
}

if (-not (Test-Path $catalogPath)) {
    throw "Catalog file not found: $catalogPath"
}

if (-not (Test-Path $mediaRoot)) {
    throw "Media folder not found: $mediaRoot"
}

Ensure-DockerEngine

if (-not $MetadataOnly) {
    $aviFiles = Get-ChildItem -Path $mediaRoot -Filter "*.avi" -Recurse -File | Sort-Object FullName
    foreach ($aviFile in $aviFiles) {
        $mp4Path = [System.IO.Path]::ChangeExtension($aviFile.FullName, ".mp4")

        if (-not (Test-Path $mp4Path)) {
            Write-Host "Converting $($aviFile.FullName) -> $mp4Path" -ForegroundColor Cyan
            Convert-AviToMp4 -InputPath $aviFile.FullName -OutputPath $mp4Path
        } else {
            Write-Host "Skipping existing MP4 for $($aviFile.Name)" -ForegroundColor Yellow
        }

        if ($DeleteOriginalAvi -and (Test-Path $mp4Path)) {
            Remove-Item $aviFile.FullName -Force
        }
    }
}

$catalog = Get-Content $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($series in $catalog) {
    if ($seriesMetadata.ContainsKey($series.slug)) {
        $metadata = $seriesMetadata[$series.slug]
        $series.title = Decode-Base64Utf8 -Value $metadata.TitleBase64

        $episodeTitleTemplate = Decode-Base64Utf8 -Value $metadata.EpisodeTitleTemplateBase64
        $episodeDescriptionTemplate = Decode-Base64Utf8 -Value $metadata.EpisodeDescriptionTemplateBase64

        foreach ($episode in $series.episodes) {
            $episode.title = $episodeTitleTemplate.Replace("{episode}", [string]$episode.episode_number).Replace("{season}", [string]$episode.season_number).Replace("{series}", [string]$series.title)
            $episode.description = $episodeDescriptionTemplate.Replace("{episode}", [string]$episode.episode_number).Replace("{season}", [string]$episode.season_number).Replace("{series}", [string]$series.title)

            if ($episode.media_path -like "*.avi") {
                $mp4Relative = [System.IO.Path]::ChangeExtension($episode.media_path, ".mp4").Replace("\", "/")
                $mp4Absolute = Join-Path $projectRoot ("media\" + $mp4Relative.Replace("/", "\"))
                if (Test-Path $mp4Absolute) {
                    $episode.media_path = $mp4Relative
                }
            }

            $videoAbsolute = Join-Path $projectRoot ("media\" + $episode.media_path.Replace("/", "\"))
            if (Test-Path $videoAbsolute) {
                $episode.duration_seconds = Get-VideoDurationSeconds -VideoPath $videoAbsolute
            }
        }
    }
}

$json = $catalog | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($catalogPath, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

Write-Host "Updated backend/catalog.json" -ForegroundColor Green

& ".\windows\run-local.ps1" -Build

Write-Host ""
if ($MetadataOnly) {
    Write-Host "Metadata refresh complete." -ForegroundColor Green
} else {
    Write-Host "Library repair complete." -ForegroundColor Green
}
Write-Host "Open http://nastenka-flix"
