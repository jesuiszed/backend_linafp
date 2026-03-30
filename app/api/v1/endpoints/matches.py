from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.club import Club
from app.models.match import Match, MatchStatus
from app.models.season import Season
from app.models.user import User, UserRole
from app.services.audit import write_audit_log
from app.schemas.match import MatchCreate, MatchRead, MatchScoreUpdate, MatchUpdate

router = APIRouter()


def _assert_match_editable(match: Match, current_user: User) -> None:
    if match.is_locked and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Match is locked")


@router.get("")
def list_matches(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    season_id: int | None = Query(default=None, ge=1),
    matchday: int | None = Query(default=None, ge=1),
) -> dict:
    query = db.query(Match)
    if season_id is not None:
        query = query.filter(Match.season_id == season_id)
    if matchday is not None:
        query = query.filter(Match.matchday == matchday)

    total = query.count()
    items = query.order_by(Match.kickoff_at.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": [MatchRead.model_validate(item).model_dump() for item in items],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "season_id": season_id,
            "matchday": matchday,
        },
    }


@router.get("/{match_id}", response_model=MatchRead)
def get_match(match_id: int, db: Session = Depends(get_db)) -> MatchRead:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return MatchRead.model_validate(match)


@router.post("", response_model=MatchRead)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchRead:
    if payload.club_home_id == payload.club_away_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Home and away clubs must be different")

    season = db.query(Season).filter(Season.id == payload.season_id).first()
    if not season:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")

    home_club = db.query(Club).filter(Club.id == payload.club_home_id).first()
    away_club = db.query(Club).filter(Club.id == payload.club_away_id).first()
    if not home_club or not away_club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")

    duplicate = (
        db.query(Match)
        .filter(
            Match.season_id == payload.season_id,
            Match.matchday == payload.matchday,
            Match.club_home_id == payload.club_home_id,
            Match.club_away_id == payload.club_away_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Match already exists")

    item = Match(**payload.model_dump())
    db.add(item)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="create",
        entity="match",
        entity_id=str(item.id),
        details=f"season={item.season_id}, matchday={item.matchday}",
    )
    db.commit()
    db.refresh(item)
    return MatchRead.model_validate(item)


@router.patch("/{match_id}", response_model=MatchRead)
def update_match(
    match_id: int,
    payload: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchRead:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    _assert_match_editable(match, current_user)

    updates = payload.model_dump(exclude_unset=True)
    next_home = updates.get("club_home_id", match.club_home_id)
    next_away = updates.get("club_away_id", match.club_away_id)
    if next_home == next_away:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Home and away clubs must be different")

    if "season_id" in updates:
        season = db.query(Season).filter(Season.id == updates["season_id"]).first()
        if not season:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season not found")

    if "club_home_id" in updates:
        if not db.query(Club).filter(Club.id == updates["club_home_id"]).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Home club not found")

    if "club_away_id" in updates:
        if not db.query(Club).filter(Club.id == updates["club_away_id"]).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Away club not found")

    for key, value in updates.items():
        setattr(match, key, value)

    db.add(match)
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="update",
        entity="match",
        entity_id=str(match.id),
        details=f"fields={','.join(sorted(updates.keys()))}",
    )
    db.commit()
    db.refresh(match)
    return MatchRead.model_validate(match)


@router.post("/{match_id}/score", response_model=MatchRead)
def set_match_score(
    match_id: int,
    payload: MatchScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchRead:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    _assert_match_editable(match, current_user)

    match.home_score_ht = payload.home_score_ht
    match.away_score_ht = payload.away_score_ht
    match.home_score_ft = payload.home_score_ft
    match.away_score_ft = payload.away_score_ft

    db.add(match)
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="set_score",
        entity="match",
        entity_id=str(match.id),
        details=f"ht={payload.home_score_ht}-{payload.away_score_ht}, ft={payload.home_score_ft}-{payload.away_score_ft}",
    )
    db.commit()
    db.refresh(match)
    return MatchRead.model_validate(match)


@router.post("/{match_id}/lock", response_model=MatchRead)
def lock_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchRead:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.is_locked = True
    if match.status != MatchStatus.FINISHED:
        match.status = MatchStatus.FINISHED

    db.add(match)
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="lock",
        entity="match",
        entity_id=str(match.id),
        details="Match locked",
    )
    db.commit()
    db.refresh(match)
    return MatchRead.model_validate(match)


@router.post("/{match_id}/unlock", response_model=MatchRead)
def unlock_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchRead:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.is_locked = False
    db.add(match)
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="unlock",
        entity="match",
        entity_id=str(match.id),
        details="Match unlocked",
    )
    db.commit()
    db.refresh(match)
    return MatchRead.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    _assert_match_editable(match, current_user)

    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="delete",
        entity="match",
        entity_id=str(match.id),
        details=f"season={match.season_id}, matchday={match.matchday}",
    )
    db.delete(match)
    db.commit()
