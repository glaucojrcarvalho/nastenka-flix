from pathlib import Path

from app.services.catalog_import import (
    build_import_operations,
    build_series_entry,
    infer_episode_number,
    slugify,
    write_series_to_catalog,
)


def test_infer_episode_number_handles_messy_scene_names() -> None:
    assert infer_episode_number("Ne.rodis.krasivoy.001.seriya.iz.200.2005-2006.DivX.DVDRip.avi") == 1
    assert infer_episode_number("Моя прекрасная няня - S01.E023 (023).mp4") == 23


def test_slugify_transliterates_cyrillic() -> None:
    assert slugify("Моя прекрасная няня") == "moya-prekrasnaya-nyanya"


def test_build_series_entry_and_write_catalog(tmp_path: Path) -> None:
    source_dir = tmp_path / "imports"
    source_dir.mkdir()
    (source_dir / "Моя прекрасная няня - S01.E001.avi").write_bytes(b"one")
    (source_dir / "Моя прекрасная няня - S01.E002.avi").write_bytes(b"two")

    media_root = tmp_path / "media"
    operations = build_import_operations(
        source_dir=source_dir,
        media_root=media_root,
        series_slug="moya-prekrasnaya-nyanya",
        season_number=1,
    )

    series_entry = build_series_entry(
        title="Моя прекрасная няня",
        slug="moya-prekrasnaya-nyanya",
        synopsis="",
        poster_url=None,
        season_number=1,
        operations=operations,
        episode_title_template="Episode {episode}",
        episode_description_template="Episode {episode}",
    )
    assert series_entry["episodes"][0]["media_path"] == "series/moya-prekrasnaya-nyanya/season-01/s01e001.avi"
    assert series_entry["episodes"][1]["media_path"] == "series/moya-prekrasnaya-nyanya/season-01/s01e002.avi"

    catalog_path = tmp_path / "catalog.json"
    write_series_to_catalog(catalog_path, series_entry)
    contents = catalog_path.read_text(encoding="utf-8")
    assert "Моя прекрасная няня" in contents
    assert "s01e001.avi" in contents
