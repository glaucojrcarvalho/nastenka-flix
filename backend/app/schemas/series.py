from pydantic import BaseModel

from app.schemas.episode import EpisodeSummary


class SeriesStats(BaseModel):
    total_episodes: int
    watched_episodes: int
    completion_percent: float


class SeriesSummary(BaseModel):
    id: int
    slug: str
    title: str
    synopsis: str
    poster_url: str | None = None
    seasons_count: int
    stats: SeriesStats


class SeriesDetail(SeriesSummary):
    episodes: list[EpisodeSummary]
