from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.season import Season
from app.services.statistics import compute_standings

router = APIRouter()


@router.get("")
def get_standings(season_id: int | None = Query(default=None, ge=1), db: Session = Depends(get_db)) -> dict:
    resolved_season_id = season_id
    if resolved_season_id is None:
        latest = db.query(Season).order_by(Season.id.desc()).first()
        if latest is None:
            return {"data": {"season_id": None, "rows": []}}
        resolved_season_id = latest.id

    return {
        "data": {
            "season_id": resolved_season_id,
            "rows": compute_standings(db, resolved_season_id),
        }
    }
