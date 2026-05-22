from app.db.database import SessionLocal, init_db
from app.db.models import Episode, Series
from app.db.seed import _load_catalog


def test_seed_updates_existing_series_and_episode_fields() -> None:
    series_fixture = _load_catalog()[0]
    episode_fixture = series_fixture["episodes"][0]

    init_db()

    with SessionLocal() as session:
        series = session.query(Series).filter(Series.slug == series_fixture["slug"]).first()
        assert series is not None
        series.title = "Wrong Title"

        episode = (
            session.query(Episode)
            .filter(Episode.series_id == series.id)
            .filter(Episode.season_number == episode_fixture["season_number"])
            .filter(Episode.episode_number == episode_fixture["episode_number"])
            .first()
        )
        assert episode is not None
        episode.title = "Broken Episode"
        session.commit()

    init_db()

    with SessionLocal() as session:
        series = session.query(Series).filter(Series.slug == series_fixture["slug"]).first()
        assert series is not None
        assert series.title == series_fixture["title"]

        episode = (
            session.query(Episode)
            .filter(Episode.series_id == series.id)
            .filter(Episode.season_number == episode_fixture["season_number"])
            .filter(Episode.episode_number == episode_fixture["episode_number"])
            .first()
        )
        assert episode is not None
        assert episode.title == episode_fixture["title"]
