from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.competition import Competition
from app.models.season import Season
from app.models.user import UserRole
from app.schemas.season import SeasonCreate, SeasonRead, SeasonUpdate

router = APIRouter()


@router.get("")
def list_seasons(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    competition_id: int | None = Query(default=None, ge=1),
) -> dict:
    query = db.query(Season)
    if competition_id is not None:
        query = query.filter(Season.competition_id == competition_id)

    total = query.count()
    items = query.order_by(Season.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": [SeasonRead.model_validate(item).model_dump() for item in items],
        "meta": {"page": page, "page_size": page_size, "total": total, "competition_id": competition_id},
    }


@router.get("/{season_id}", response_model=SeasonRead)
def get_season(season_id: int, db: Session = Depends(get_db)) -> SeasonRead:
    item = db.query(Season).filter(Season.id == season_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")
    return SeasonRead.model_validate(item)


@router.post("", response_model=SeasonRead)
def create_season(
    payload: SeasonCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> SeasonRead:
    competition = db.query(Competition).filter(Competition.id == payload.competition_id).first()
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")

    duplicate = db.query(Season).filter(Season.competition_id == payload.competition_id, Season.label == payload.label).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Season label already exists for this competition")

    item = Season(
        competition_id=payload.competition_id,
        label=payload.label,
        points_win=payload.points_win,
        points_draw=payload.points_draw,
        points_loss=payload.points_loss,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return SeasonRead.model_validate(item)


@router.patch("/{season_id}", response_model=SeasonRead)
def update_season(
    season_id: int,
    payload: SeasonUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> SeasonRead:
    item = db.query(Season).filter(Season.id == season_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")

    updates = payload.model_dump(exclude_unset=True)

    if "competition_id" in updates:
        competition = db.query(Competition).filter(Competition.id == updates["competition_id"]).first()
        if not competition:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")

    next_competition_id = updates.get("competition_id", item.competition_id)
    next_label = updates.get("label", item.label)
    duplicate = (
        db.query(Season)
        .filter(
            Season.competition_id == next_competition_id,
            Season.label == next_label,
            Season.id != season_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Season label already exists for this competition")

    for key, value in updates.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return SeasonRead.model_validate(item)


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season(
    season_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    item = db.query(Season).filter(Season.id == season_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")

    db.delete(item)
    db.commit()
