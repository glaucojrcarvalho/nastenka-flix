from pydantic import BaseModel


class EpisodeSummary(BaseModel):
    id: int
    series_slug: str
    season_number: int
    episode_number: int
    title: str
    description: str
    duration_seconds: int
    media_url: str


class EpisodeDetail(EpisodeSummary):
    thumbnail_url: str | None = None
