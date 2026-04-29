from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Series, User
from app.schemas.series import SeriesDetail, SeriesSummary
from app.services.progress_service import build_series_detail, build_series_summaries

router = APIRouter(prefix="/series", tags=["series"])


@router.get("/", response_model=list[SeriesSummary])
def list_series(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SeriesSummary]:
    series_items = db.query(Series).options(joinedload(Series.episodes)).order_by(Series.title.asc()).all()
    return build_series_summaries(series_items, current_user.id, db)


@router.get("/{series_slug}", response_model=SeriesDetail)
def get_series(
    series_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SeriesDetail:
    series = (
        db.query(Series)
        .options(joinedload(Series.episodes))
        .filter(Series.slug == series_slug)
        .first()
    )
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")

    return build_series_detail(series, current_user.id, db)
