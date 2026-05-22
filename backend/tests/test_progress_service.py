from app.db.database import SessionLocal, init_db
from app.db.models import Episode, Series, User, WatchProgress
from app.schemas.progress import ProgressUpdate
from app.services.progress_service import save_progress


def test_unknown_duration_does_not_mark_episode_completed() -> None:
    init_db()

    with SessionLocal() as session:
        user = session.query(User).first()
        assert user is not None

        series = Series(
            slug="duration-test-series",
            title="Duration Test Series",
            synopsis="",
            poster_url=None,
            seasons_count=1,
        )
        session.add(series)
        session.flush()

        episode = Episode(
            series_id=series.id,
            season_number=1,
            episode_number=1,
            title="Episode 1",
            description="",
            duration_seconds=0,
            media_path="series/duration-test-series/season-01/s01e001.mp4",
            thumbnail_url=None,
        )
        session.add(episode)
        session.commit()
        session.refresh(episode)

        response = save_progress(
            session,
            user.id,
            episode,
            ProgressUpdate(position_seconds=1, completed=False),
        )

        assert response.completed is False

        persisted = (
            session.query(WatchProgress)
            .filter(WatchProgress.user_id == user.id, WatchProgress.episode_id == episode.id)
            .first()
        )
        assert persisted is not None
        assert persisted.completed is False
