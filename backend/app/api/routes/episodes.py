from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Episode, Series, User
from app.schemas.episode import EpisodeDetail, EpisodeSummary
from app.services.media_service import episode_to_detail, episode_to_summary

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/by-series/{series_slug}", response_model=list[EpisodeSummary])
def get_series_episodes(
    series_slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[EpisodeSummary]:
    series = db.query(Series).options(joinedload(Series.episodes)).filter(Series.slug == series_slug).first()
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return [episode_to_summary(episode) for episode in sorted(series.episodes, key=lambda item: (item.season_number, item.episode_number))]


@router.get("/{episode_id}", response_model=EpisodeDetail)
def get_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> EpisodeDetail:
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode_to_detail(episode)
