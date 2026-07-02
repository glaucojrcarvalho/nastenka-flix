#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.catalog_import import infer_episode_number  # noqa: E402


@dataclass(frozen=True)
class SeriesConfig:
    slug: str
    title: str
    source_folder: str | None = None
    season_number: int = 1
    episode_title_template: str = "Серия {episode}"
    episode_description_template: str = "Серия {episode}"


SERIES_CONFIGS: tuple[SeriesConfig, ...] = (
    SeriesConfig(
        slug="ne-rodis-krasivoy",
        title="Не родись красивой",
        source_folder="Ne.rodis.krasivoy.200.seriy.iz.200.2005-2006.DivX.DVDRip",
    ),
    SeriesConfig(
        slug="moya-prekrasnaya-nyanya",
        title="Моя прекрасная няня",
        source_folder="Моя прекрасная няня DVDRip",
    ),
)

VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".wmv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import and repair the Ubuntu media library from ~/Downloads/series."
    )
    parser.add_argument(
        "--source-root",
        default=str(Path.home() / "Downloads" / "series"),
        help="Folder containing the source series directories. Defaults to ~/Downloads/series.",
    )
    parser.add_argument(
        "--delete-original-avi",
        action="store_true",
        help="Deprecated. AVI source files are now deleted automatically after a successful conversion.",
    )
    parser.add_argument(
        "--skip-restart",
        action="store_true",
        help="Do not restart docker compose at the end.",
    )
    parser.add_argument(
        "--series-slug",
        choices=tuple(config.slug for config in SERIES_CONFIGS),
        help="Import only one configured series. Useful when ~/Downloads/series contains one flat set of episode files.",
    )
    parser.add_argument(
        "--flat-files",
        action="store_true",
        help="Read episode files directly from --source-root instead of expecting a subfolder per series.",
    )
    return parser.parse_args()


def ensure_docker() -> None:
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit("Docker is required and must be running.") from exc


def discover_source_files(source_dir: Path) -> list[Path]:
    files = [path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS]
    if not files:
        raise SystemExit(f"No supported video files found in {source_dir}")
    return sorted(files)


def convert_to_mp4(source_file: Path, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{source_file.parent}:/source:ro",
        "-v",
        f"{ROOT_DIR}:/workspace",
        "-w",
        "/workspace",
        "jrottenberg/ffmpeg:6.0-ubuntu",
        "-y",
        "-i",
        f"/source/{source_file.name}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        f"/workspace/{output_file.relative_to(ROOT_DIR).as_posix()}",
    ]
    subprocess.run(docker_cmd, check=True)


def probe_duration_seconds(video_file: Path) -> int:
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT_DIR}:/workspace",
        "-w",
        "/workspace",
        "--entrypoint",
        "ffprobe",
        "jrottenberg/ffmpeg:6.0-ubuntu",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        f"/workspace/{video_file.relative_to(ROOT_DIR).as_posix()}",
    ]
    result = subprocess.run(docker_cmd, check=True, capture_output=True, text=True)
    duration_value = result.stdout.strip()
    if not duration_value:
        return 0
    return max(0, math.floor(float(duration_value)))


def load_catalog(catalog_path: Path) -> list[dict]:
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def save_catalog(catalog_path: Path, catalog: list[dict]) -> None:
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def repair_catalog_series(catalog: list[dict], series_config: SeriesConfig, operations: list[tuple[int, Path, int]]) -> None:
    series = next((item for item in catalog if item.get("slug") == series_config.slug), None)
    if series is None:
        series = {
            "slug": series_config.slug,
            "title": series_config.title,
            "synopsis": "",
            "poster_url": None,
            "seasons_count": series_config.season_number,
            "episodes": [],
        }
        catalog.append(series)

    series["title"] = series_config.title
    series["seasons_count"] = max(int(series.get("seasons_count", 1)), series_config.season_number)

    episodes_by_key = {
        (int(episode["season_number"]), int(episode["episode_number"])): episode
        for episode in series.get("episodes", [])
    }

    for episode_number, output_file, duration_seconds in operations:
        key = (series_config.season_number, episode_number)
        episode = episodes_by_key.get(key)
        if episode is None:
            episode = {
                "season_number": series_config.season_number,
                "episode_number": episode_number,
                "duration_seconds": duration_seconds,
                "media_path": "",
            }
            series.setdefault("episodes", []).append(episode)
            episodes_by_key[key] = episode

        episode["title"] = series_config.episode_title_template.format(
            episode=episode_number,
            season=series_config.season_number,
            series=series_config.title,
        )
        episode["description"] = series_config.episode_description_template.format(
            episode=episode_number,
            season=series_config.season_number,
            series=series_config.title,
        )
        episode["duration_seconds"] = duration_seconds
        episode["media_path"] = output_file.relative_to(ROOT_DIR / "media").as_posix()

    series["episodes"] = sorted(
        series.get("episodes", []),
        key=lambda episode: (int(episode["season_number"]), int(episode["episode_number"])),
    )


def restart_stack() -> None:
    subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=ROOT_DIR, check=True)


def resolve_series_configs(args: argparse.Namespace) -> list[SeriesConfig]:
    if args.series_slug:
        matching = [config for config in SERIES_CONFIGS if config.slug == args.series_slug]
        return matching
    return list(SERIES_CONFIGS)


def main() -> int:
    args = parse_args()
    ensure_docker()

    source_root = Path(args.source_root).expanduser().resolve()
    catalog_path = ROOT_DIR / "backend" / "catalog.json"
    media_root = ROOT_DIR / "media"

    if not source_root.exists():
        raise SystemExit(f"Source root not found: {source_root}")
    if not catalog_path.exists():
        raise SystemExit(f"Catalog file not found: {catalog_path}")

    catalog = load_catalog(catalog_path)

    series_configs = resolve_series_configs(args)

    if args.flat_files and len(series_configs) != 1:
        raise SystemExit("--flat-files requires exactly one target series. Pass --series-slug.")

    for series_config in series_configs:
        source_dir = source_root if args.flat_files else source_root / str(series_config.source_folder)
        if not source_dir.exists():
            print(f"Skipping missing source folder: {source_dir}")
            continue

        print(f"\nProcessing {series_config.title}")
        operations: list[tuple[int, Path, int]] = []

        for source_file in discover_source_files(source_dir):
            episode_number = infer_episode_number(source_file.name)
            output_file = (
                media_root
                / "series"
                / series_config.slug
                / f"season-{series_config.season_number:02d}"
                / f"s{series_config.season_number:02d}e{episode_number:03d}.mp4"
            )

            if output_file.exists():
                print(f"Skipping existing MP4: {output_file}")
            else:
                print(f"Converting {source_file.name} -> {output_file.name}")
                convert_to_mp4(source_file, output_file)

            if source_file.suffix.lower() == ".avi" and output_file.exists():
                source_file.unlink()

            duration_seconds = probe_duration_seconds(output_file) if output_file.exists() else 0
            operations.append((episode_number, output_file, duration_seconds))

        repair_catalog_series(catalog, series_config, operations)

    save_catalog(catalog_path, catalog)
    print(f"\nUpdated catalog: {catalog_path}")

    if not args.skip_restart:
        restart_stack()
        print("Docker compose restarted.")

    print("Ubuntu library repair complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
