from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.player import Player
from app.models.user import UserRole
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate

router = APIRouter()


@router.get("")
def list_players(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
) -> dict:
    query = db.query(Player)
    if q:
        query = query.filter((Player.first_name + " " + Player.last_name).ilike(f"%{q}%"))

    total = query.count()
    items = query.order_by(Player.last_name.asc(), Player.first_name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": [PlayerRead.model_validate(item).model_dump() for item in items],
        "meta": {"page": page, "page_size": page_size, "total": total, "q": q},
    }


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    item = db.query(Player).filter(Player.id == player_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return PlayerRead.model_validate(item)


@router.post("", response_model=PlayerRead)
def create_player(
    payload: PlayerCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> PlayerRead:
    item = Player(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return PlayerRead.model_validate(item)


@router.patch("/{player_id}", response_model=PlayerRead)
def update_player(
    player_id: int,
    payload: PlayerUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> PlayerRead:
    item = db.query(Player).filter(Player.id == player_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return PlayerRead.model_validate(item)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    item = db.query(Player).filter(Player.id == player_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    db.delete(item)
    db.commit()
