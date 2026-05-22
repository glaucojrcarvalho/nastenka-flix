#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT_DIR / "backend" / "catalog.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update one series entry in backend/catalog.json without moving media files.")
    parser.add_argument("--series-slug", required=True, help="Series slug to update.")
    parser.add_argument("--series-title", required=True, help="New display title.")
    parser.add_argument("--synopsis", default=None, help="Optional replacement synopsis.")
    parser.add_argument("--episode-title-template", default=None, help="Template for all episode titles.")
    parser.add_argument("--episode-description-template", default=None, help="Template for all episode descriptions.")
    parser.add_argument("--catalog-path", default=str(CATALOG_PATH), help="Catalog path. Defaults to ./backend/catalog.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog_path).expanduser().resolve()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    updated = False
    for series in catalog:
        if series.get("slug") != args.series_slug:
            continue

        series["title"] = args.series_title
        if args.synopsis is not None:
            series["synopsis"] = args.synopsis

        for episode in series.get("episodes", []):
            if args.episode_title_template is not None:
                episode["title"] = args.episode_title_template.format(
                    episode=episode["episode_number"],
                    season=episode["season_number"],
                    series=args.series_title,
                )
            if args.episode_description_template is not None:
                episode["description"] = args.episode_description_template.format(
                    episode=episode["episode_number"],
                    season=episode["season_number"],
                    series=args.series_title,
                )

        updated = True
        break

    if not updated:
        raise SystemExit(f"Series slug not found: {args.series_slug}")

    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated series metadata for {args.series_slug} in {catalog_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
