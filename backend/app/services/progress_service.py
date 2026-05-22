from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import Episode, Series, WatchProgress
from app.schemas.progress import ProgressResponse, ProgressUpdate
from app.schemas.series import SeriesDetail, SeriesStats, SeriesSummary
from app.services.media_service import episode_to_summary


def get_progress_for_episode(db: Session, user_id: int, episode_id: int) -> ProgressResponse:
    progress = (
        db.query(WatchProgress)
        .filter(WatchProgress.user_id == user_id, WatchProgress.episode_id == episode_id)
        .first()
    )
    if progress is None:
        return ProgressResponse(episode_id=episode_id, position_seconds=0, completed=False)
    return ProgressResponse(
        episode_id=episode_id,
        position_seconds=progress.position_seconds,
        completed=progress.completed,
    )


def save_progress(db: Session, user_id: int, episode: Episode, payload: ProgressUpdate) -> ProgressResponse:
    progress = (
        db.query(WatchProgress)
        .filter(WatchProgress.user_id == user_id, WatchProgress.episode_id == episode.id)
        .first()
    )
    if progress is None:
        progress = WatchProgress(user_id=user_id, episode_id=episode.id)
        db.add(progress)

    has_known_duration = episode.duration_seconds > 0
    progress.position_seconds = min(payload.position_seconds, episode.duration_seconds) if has_known_duration else payload.position_seconds
    progress.completed = payload.completed or (
        has_known_duration and progress.position_seconds >= max(episode.duration_seconds - 30, 0)
    )
    progress.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(progress)

    return ProgressResponse(
        episode_id=episode.id,
        position_seconds=progress.position_seconds,
        completed=progress.completed,
    )


def build_series_summaries(series_items: list[Series], user_id: int, db: Session) -> list[SeriesSummary]:
    summaries: list[SeriesSummary] = []
    for series in series_items:
        stats = build_series_stats(series, user_id, db)
        summaries.append(
            SeriesSummary(
                id=series.id,
                slug=series.slug,
                title=series.title,
                synopsis=series.synopsis,
                poster_url=series.poster_url,
                seasons_count=series.seasons_count,
                stats=stats,
            )
        )
    return summaries


def build_series_detail(series: Series, user_id: int, db: Session) -> SeriesDetail:
    ordered_episodes = sorted(series.episodes, key=lambda item: (item.season_number, item.episode_number))
    return SeriesDetail(
        id=series.id,
        slug=series.slug,
        title=series.title,
        synopsis=series.synopsis,
        poster_url=series.poster_url,
        seasons_count=series.seasons_count,
        stats=build_series_stats(series, user_id, db),
        episodes=[episode_to_summary(episode) for episode in ordered_episodes],
    )


def build_series_stats(series: Series, user_id: int, db: Session) -> SeriesStats:
    total_episodes = len(series.episodes)
    if total_episodes == 0:
        return SeriesStats(total_episodes=0, watched_episodes=0, completion_percent=0)

    episode_ids = [episode.id for episode in series.episodes]
    watched_episodes = (
        db.query(WatchProgress)
        .filter(
            WatchProgress.user_id == user_id,
            WatchProgress.episode_id.in_(episode_ids),
            WatchProgress.completed.is_(True),
        )
        .count()
    )
    completion_percent = round((watched_episodes / total_episodes) * 100, 2)
    return SeriesStats(
        total_episodes=total_episodes,
        watched_episodes=watched_episodes,
        completion_percent=completion_percent,
    )
