from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Episode, User
from app.schemas.progress import ProgressResponse, ProgressUpdate
from app.services.progress_service import get_progress_for_episode, save_progress

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/episodes/{episode_id}", response_model=ProgressResponse)
def get_episode_progress(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return get_progress_for_episode(db, current_user.id, episode_id)


@router.post("/episodes/{episode_id}", response_model=ProgressResponse)
def update_episode_progress(
    episode_id: int,
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return save_progress(db, current_user.id, episode, payload)
