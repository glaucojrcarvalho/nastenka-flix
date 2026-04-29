from app.db.models import Episode
from app.schemas.episode import EpisodeDetail, EpisodeSummary


def build_media_url(media_path: str) -> str:
    normalized = media_path.lstrip("/")
    return f"/media/{normalized}"


def episode_to_summary(episode: Episode) -> EpisodeSummary:
    return EpisodeSummary(
        id=episode.id,
        series_slug=episode.series.slug,
        season_number=episode.season_number,
        episode_number=episode.episode_number,
        title=episode.title,
        description=episode.description,
        duration_seconds=episode.duration_seconds,
        media_url=build_media_url(episode.media_path),
    )


def episode_to_detail(episode: Episode) -> EpisodeDetail:
    summary = episode_to_summary(episode)
    return EpisodeDetail(**summary.model_dump(), thumbnail_url=episode.thumbnail_url)
