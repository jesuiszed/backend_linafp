from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.season import Season
from app.services.statistics import card_stats, club_form, player_summary, top_assists, top_scorers

router = APIRouter()


def _resolve_season_id(db: Session, season_id: int | None) -> int | None:
    if season_id is not None:
        return season_id

    latest = db.query(Season).order_by(Season.id.desc()).first()
    if latest is None:
        return None
    return latest.id


@router.get("/top-scorers")
def get_top_scorers(
    season_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    resolved = _resolve_season_id(db, season_id)
    if resolved is None:
        return {"data": []}
    return {"data": top_scorers(db, resolved, limit)}


@router.get("/top-assists")
def get_top_assists(
    season_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    resolved = _resolve_season_id(db, season_id)
    if resolved is None:
        return {"data": []}
    return {"data": top_assists(db, resolved, limit)}


@router.get("/cards")
def get_cards(
    season_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> dict:
    resolved = _resolve_season_id(db, season_id)
    if resolved is None:
        return {"data": {"by_club": [], "by_player": []}}
    return {"data": card_stats(db, resolved)}


@router.get("/club-form")
def get_club_form(
    season_id: int | None = Query(default=None, ge=1),
    club_id: int = Query(..., ge=1),
    last: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> dict:
    resolved = _resolve_season_id(db, season_id)
    if resolved is None:
        return {"data": {"club_id": club_id, "season_id": None, "last": last, "form": []}}
    return {"data": club_form(db, resolved, club_id, last)}


@router.get("/player-summary")
def get_player_summary(
    season_id: int | None = Query(default=None, ge=1),
    player_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> dict:
    resolved = _resolve_season_id(db, season_id)
    if resolved is None:
        return {
            "data": {
                "player_id": player_id,
                "season_id": None,
                "goals": 0,
                "assists": 0,
                "yellow_cards": 0,
                "red_cards": 0,
                "involved_matches": 0,
            }
        }
    return {"data": player_summary(db, resolved, player_id)}
