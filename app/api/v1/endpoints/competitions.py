from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.competition import Competition
from app.models.user import UserRole
from app.schemas.competition import CompetitionCreate, CompetitionRead, CompetitionUpdate

router = APIRouter()


@router.get("")
def list_competitions(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
) -> dict:
    query = db.query(Competition)
    if q:
        query = query.filter(Competition.name.ilike(f"%{q}%"))

    total = query.count()
    items = query.order_by(Competition.name.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": [CompetitionRead.model_validate(item).model_dump() for item in items],
        "meta": {"page": page, "page_size": page_size, "total": total, "q": q},
    }


@router.get("/{competition_id}", response_model=CompetitionRead)
def get_competition(competition_id: int, db: Session = Depends(get_db)) -> CompetitionRead:
    item = db.query(Competition).filter(Competition.id == competition_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")
    return CompetitionRead.model_validate(item)


@router.post("", response_model=CompetitionRead)
def create_competition(
    payload: CompetitionCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> CompetitionRead:
    existing = db.query(Competition).filter(Competition.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Competition name already exists")

    item = Competition(name=payload.name, is_archived=payload.is_archived)
    db.add(item)
    db.commit()
    db.refresh(item)
    return CompetitionRead.model_validate(item)


@router.patch("/{competition_id}", response_model=CompetitionRead)
def update_competition(
    competition_id: int,
    payload: CompetitionUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> CompetitionRead:
    item = db.query(Competition).filter(Competition.id == competition_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates:
        duplicate = db.query(Competition).filter(Competition.name == updates["name"], Competition.id != competition_id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Competition name already exists")

    for key, value in updates.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return CompetitionRead.model_validate(item)


@router.delete("/{competition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    item = db.query(Competition).filter(Competition.id == competition_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")

    db.delete(item)
    db.commit()
