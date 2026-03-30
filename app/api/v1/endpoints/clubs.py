from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.club import Club
from app.models.user import UserRole
from app.schemas.club import ClubCreate, ClubRead, ClubUpdate

router = APIRouter()


@router.get("")
def list_clubs(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
) -> dict:
    query = db.query(Club)
    if q:
        query = query.filter(Club.name.ilike(f"%{q}%"))

    total = query.count()
    clubs = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [ClubRead.model_validate(club).model_dump() for club in clubs],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "q": q,
        },
    }


@router.post("", response_model=ClubRead)
def create_club(
    payload: ClubCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> ClubRead:
    existing = db.query(Club).filter(Club.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")

    club = Club(
        name=payload.name,
        city=payload.city,
        stadium=payload.stadium,
        logo_url=payload.logo_url,
    )
    db.add(club)
    db.commit()
    db.refresh(club)
    return ClubRead.model_validate(club)


@router.get("/{club_id}", response_model=ClubRead)
def get_club(club_id: int, db: Session = Depends(get_db)) -> ClubRead:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    return ClubRead.model_validate(club)


@router.patch("/{club_id}", response_model=ClubRead)
def update_club(
    club_id: int,
    payload: ClubUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> ClubRead:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates:
        duplicate = db.query(Club).filter(Club.name == updates["name"], Club.id != club_id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")

    for key, value in updates.items():
        setattr(club, key, value)

    db.add(club)
    db.commit()
    db.refresh(club)
    return ClubRead.model_validate(club)


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")

    db.delete(club)
    db.commit()
