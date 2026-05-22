from __future__ import annotations

import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS = {
    ".avi",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".wmv",
}

_CYRILLIC_MAP = str.maketrans(
    {
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Ґ": "G",
        "Д": "D",
        "Е": "E",
        "Є": "Ye",
        "Ё": "Yo",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "І": "I",
        "Ї": "Yi",
        "Й": "Y",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "Kh",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Shch",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ye",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "і": "i",
        "ї": "yi",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
)


@dataclass(frozen=True)
class ImportOperation:
    source: Path
    destination: Path
    episode_number: int


def slugify(value: str) -> str:
    transliterated = value.translate(_CYRILLIC_MAP)
    normalized = unicodedata.normalize("NFKD", transliterated)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "series"


def infer_episode_number(filename: str) -> int:
    season_episode_match = re.search(r"[Ss](\d{1,2})[ ._-]?[Ee](\d{1,3})", filename)
    if season_episode_match:
        return int(season_episode_match.group(2))

    episode_match = re.search(r"(?:^|[^a-zA-Z])(?:ep|episode|e)(\d{1,3})(?:[^a-zA-Z]|$)", filename, re.IGNORECASE)
    if episode_match:
        return int(episode_match.group(1))

    three_digit_groups = re.findall(r"(?<!\d)(\d{3})(?!\d)", filename)
    if three_digit_groups:
        return int(three_digit_groups[0])

    one_or_two_digit_groups = re.findall(r"(?<!\d)(\d{1,2})(?!\d)", filename)
    if one_or_two_digit_groups:
        return int(one_or_two_digit_groups[0])

    raise ValueError(f"Could not infer episode number from '{filename}'")


def discover_video_files(source_dir: Path) -> list[Path]:
    files = [path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS]
    if not files:
        raise FileNotFoundError(f"No supported video files found in {source_dir}")
    return sorted(files)


def build_import_operations(
    source_dir: Path,
    media_root: Path,
    series_slug: str,
    season_number: int,
) -> list[ImportOperation]:
    operations: list[ImportOperation] = []

    for source in discover_video_files(source_dir):
        episode_number = infer_episode_number(source.name)
        extension = source.suffix.lower()
        destination = media_root / "series" / series_slug / f"season-{season_number:02d}" / f"s{season_number:02d}e{episode_number:03d}{extension}"
        operations.append(ImportOperation(source=source, destination=destination, episode_number=episode_number))

    operations.sort(key=lambda operation: operation.episode_number)

    seen_numbers: set[int] = set()
    for operation in operations:
        if operation.episode_number in seen_numbers:
            raise ValueError(f"Duplicate episode number detected: {operation.episode_number}")
        seen_numbers.add(operation.episode_number)

    return operations


def apply_import_operations(operations: list[ImportOperation], mode: str) -> None:
    for operation in operations:
        operation.destination.parent.mkdir(parents=True, exist_ok=True)
        if operation.destination.exists():
            raise FileExistsError(f"Destination file already exists: {operation.destination}")

        if mode == "copy":
            shutil.copy2(operation.source, operation.destination)
        elif mode == "move":
            shutil.move(str(operation.source), str(operation.destination))
        else:
            raise ValueError(f"Unsupported mode: {mode}")


def build_series_entry(
    *,
    title: str,
    slug: str,
    synopsis: str,
    poster_url: str | None,
    season_number: int,
    operations: list[ImportOperation],
    episode_title_template: str,
    episode_description_template: str,
) -> dict:
    return {
        "slug": slug,
        "title": title,
        "synopsis": synopsis,
        "poster_url": poster_url,
        "seasons_count": season_number,
        "episodes": [
            {
                "season_number": season_number,
                "episode_number": operation.episode_number,
                "title": episode_title_template.format(episode=operation.episode_number, season=season_number, series=title),
                "description": episode_description_template.format(
                    episode=operation.episode_number,
                    season=season_number,
                    series=title,
                ),
                "duration_seconds": 0,
                "media_path": operation.destination.relative_to(operation.destination.parents[3]).as_posix(),
            }
            for operation in operations
        ],
    }


def write_series_to_catalog(catalog_path: Path, series_entry: dict) -> None:
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    else:
        catalog = []

    existing_series = next((series for series in catalog if series.get("slug") == series_entry["slug"]), None)
    filtered_catalog = [series for series in catalog if series.get("slug") != series_entry["slug"]]

    if existing_series is not None:
        imported_pairs = {
            (episode["season_number"], episode["episode_number"])
            for episode in series_entry["episodes"]
        }
        preserved_episodes = [
            episode
            for episode in existing_series.get("episodes", [])
            if (episode.get("season_number"), episode.get("episode_number")) not in imported_pairs
        ]
        merged_series = {
            **existing_series,
            **series_entry,
            "seasons_count": max(int(existing_series.get("seasons_count", 1)), int(series_entry.get("seasons_count", 1))),
            "episodes": sorted(
                [*preserved_episodes, *series_entry["episodes"]],
                key=lambda episode: (int(episode["season_number"]), int(episode["episode_number"])),
            ),
        }
        filtered_catalog.append(merged_series)
    else:
        filtered_catalog.append(series_entry)

    filtered_catalog.sort(key=lambda series: str(series.get("title", "")).casefold())

    catalog_path.write_text(json.dumps(filtered_catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
