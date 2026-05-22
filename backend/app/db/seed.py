import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.core.security import get_password_hash
from app.db.models import Episode, Series, User

# Catalog is loaded from catalog.json (gitignored, deploy-specific) when present,
# falling back to catalog.example.json (committed, contains fictional placeholder data).
_CATALOG_DIR = Path(__file__).resolve().parents[2]

def _load_catalog() -> list[dict]:
    private = _CATALOG_DIR / "catalog.json"
    fallback = _CATALOG_DIR / "catalog.example.json"
    path = private if private.exists() else fallback
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_database(db: Session) -> None:
    settings = get_settings()

    legacy_sample = db.query(Series).filter(Series.slug == "friends").first()
    if legacy_sample is not None:
        db.delete(legacy_sample)
        db.flush()

    user = db.query(User).filter(User.username == settings.demo_username).first()
    if user is None:
        db.add(
            User(
                username=settings.demo_username,
                display_name=settings.demo_display_name,
                password_hash=get_password_hash(settings.demo_password),
            )
        )
        db.flush()

    for series_fixture in _load_catalog():
        series = db.query(Series).filter(Series.slug == series_fixture["slug"]).first()
        if series is None:
            series = Series(
                slug=series_fixture["slug"],
                title=series_fixture["title"],
                synopsis=series_fixture["synopsis"],
                poster_url=series_fixture["poster_url"],
                seasons_count=series_fixture["seasons_count"],
            )
            db.add(series)
            db.flush()
        else:
            series.title = series_fixture["title"]
            series.synopsis = series_fixture["synopsis"]
            series.poster_url = series_fixture["poster_url"]
            series.seasons_count = series_fixture["seasons_count"]

        for episode_fixture in series_fixture["episodes"]:
            episode = (
                db.query(Episode)
                .filter(Episode.series_id == series.id)
                .filter(Episode.season_number == episode_fixture["season_number"])
                .filter(Episode.episode_number == episode_fixture["episode_number"])
                .first()
            )
            if episode is None:
                db.add(Episode(series_id=series.id, **episode_fixture))
                continue

            episode.title = episode_fixture["title"]
            episode.description = episode_fixture["description"]
            episode.duration_seconds = episode_fixture["duration_seconds"]
            episode.media_path = episode_fixture["media_path"]
            episode.thumbnail_url = episode_fixture.get("thumbnail_url")

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
