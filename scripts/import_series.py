#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.catalog_import import (  # noqa: E402
    apply_import_operations,
    build_import_operations,
    build_series_entry,
    slugify,
    write_series_to_catalog,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a season folder into Nastenka Flix by cleaning filenames and updating backend/catalog.json."
    )
    parser.add_argument("--source-dir", required=True, help="Folder containing the original episode video files.")
    parser.add_argument("--series-title", required=True, help="Display title used in the catalog.")
    parser.add_argument("--series-slug", help="Optional catalog slug. Defaults to a slugified version of the title.")
    parser.add_argument("--season-number", type=int, default=1, help="Season number for the imported folder.")
    parser.add_argument("--synopsis", default="", help="Series synopsis to save in the catalog.")
    parser.add_argument("--poster-url", default=None, help="Poster image URL for the series.")
    parser.add_argument(
        "--mode",
        choices=("copy", "move"),
        default="copy",
        help="Use copy to keep the originals, or move to avoid duplicating large files.",
    )
    parser.add_argument(
        "--media-root",
        default=str(ROOT_DIR / "media"),
        help="Project media root. Defaults to ./media from the repository root.",
    )
    parser.add_argument(
        "--catalog-path",
        default=str(ROOT_DIR / "backend" / "catalog.json"),
        help="Catalog file to create or update. Defaults to ./backend/catalog.json.",
    )
    parser.add_argument(
        "--episode-title-template",
        default="Episode {episode}",
        help="Template for episode titles. Available placeholders: {episode}, {season}, {series}.",
    )
    parser.add_argument(
        "--episode-description-template",
        default="Episode {episode} from season {season} of {series}.",
        help="Template for episode descriptions. Available placeholders: {episode}, {season}, {series}.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned rename and catalog output without copying or moving files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    media_root = Path(args.media_root).expanduser().resolve()
    catalog_path = Path(args.catalog_path).expanduser().resolve()
    series_slug = args.series_slug or slugify(args.series_title)

    operations = build_import_operations(
        source_dir=source_dir,
        media_root=media_root,
        series_slug=series_slug,
        season_number=args.season_number,
    )
    series_entry = build_series_entry(
        title=args.series_title,
        slug=series_slug,
        synopsis=args.synopsis,
        poster_url=args.poster_url,
        season_number=args.season_number,
        operations=operations,
        episode_title_template=args.episode_title_template,
        episode_description_template=args.episode_description_template,
    )

    print(f"Series: {args.series_title} ({series_slug})")
    print(f"Mode: {args.mode}")
    for operation in operations:
        print(f"  E{operation.episode_number:03d}: {operation.source.name} -> {operation.destination}")

    if args.dry_run:
        print(f"\nDry run only. Catalog entry would be written to {catalog_path}.")
        return 0

    apply_import_operations(operations, args.mode)
    write_series_to_catalog(catalog_path, series_entry)

    print(f"\nImported {len(operations)} episode files.")
    print(f"Updated catalog: {catalog_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
