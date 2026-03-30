from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.match import Match
from app.models.match_event import MatchEvent, MatchEventType
from app.models.player import Player
from app.models.squad_membership import SquadMembership
from app.models.user import User, UserRole
from app.services.audit import write_audit_log
from app.schemas.match_event import MatchEventCreate, MatchEventRead, MatchEventUpdate

router = APIRouter()


def _get_match_or_404(db: Session, match_id: int) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


def _assert_team_and_players_are_valid(db: Session, match: Match, payload: MatchEventCreate | MatchEventUpdate) -> None:
    team_id = payload.team_id
    player_id = payload.player_id
    related_player_id = payload.related_player_id
    event_type = payload.event_type

    if team_id is None or player_id is None or event_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="team_id, player_id and event_type are required")

    if team_id not in {match.club_home_id, match.club_away_id}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event team is not part of this match")

    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    membership = (
        db.query(SquadMembership)
        .filter(
            SquadMembership.player_id == player_id,
            SquadMembership.club_id == team_id,
            SquadMembership.season_id == match.season_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player does not belong to the selected team for this season",
        )

    if event_type == MatchEventType.SUBSTITUTION and related_player_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="related_player_id is required for substitution")

    if related_player_id is not None:
        related_player = db.query(Player).filter(Player.id == related_player_id).first()
        if not related_player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related player not found")
        related_membership = (
            db.query(SquadMembership)
            .filter(
                SquadMembership.player_id == related_player_id,
                SquadMembership.club_id == team_id,
                SquadMembership.season_id == match.season_id,
            )
            .first()
        )
        if not related_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Related player does not belong to the selected team for this season",
            )


def _assert_match_editable(match: Match, current_user: User) -> None:
    if match.is_locked and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Match is locked")


@router.get("/matches/{match_id}/events")
def list_match_events(match_id: int, db: Session = Depends(get_db)) -> dict:
    _ = _get_match_or_404(db, match_id)
    items = db.query(MatchEvent).filter(MatchEvent.match_id == match_id).order_by(MatchEvent.minute.asc(), MatchEvent.id.asc()).all()
    return {"data": [MatchEventRead.model_validate(item).model_dump() for item in items]}


@router.post("/matches/{match_id}/events", response_model=MatchEventRead)
def create_match_event(
    match_id: int,
    payload: MatchEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchEventRead:
    match = _get_match_or_404(db, match_id)
    _assert_match_editable(match, current_user)
    _assert_team_and_players_are_valid(db, match, payload)

    item = MatchEvent(match_id=match_id, **payload.model_dump())
    db.add(item)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="create",
        entity="match_event",
        entity_id=str(item.id),
        details=f"match_id={match_id}, type={item.event_type.value}, minute={item.minute}",
    )
    db.commit()
    db.refresh(item)
    return MatchEventRead.model_validate(item)


@router.patch("/matches/{match_id}/events/{event_id}", response_model=MatchEventRead)
def update_match_event(
    match_id: int,
    event_id: int,
    payload: MatchEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> MatchEventRead:
    match = _get_match_or_404(db, match_id)
    _assert_match_editable(match, current_user)

    item = db.query(MatchEvent).filter(MatchEvent.id == event_id, MatchEvent.match_id == match_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match event not found")

    updates = payload.model_dump(exclude_unset=True)
    merged = MatchEventCreate(
        team_id=updates.get("team_id", item.team_id),
        player_id=updates.get("player_id", item.player_id),
        related_player_id=updates.get("related_player_id", item.related_player_id),
        event_type=updates.get("event_type", item.event_type),
        minute=updates.get("minute", item.minute),
    )
    _assert_team_and_players_are_valid(db, match, merged)

    for key, value in updates.items():
        setattr(item, key, value)

    db.add(item)
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="update",
        entity="match_event",
        entity_id=str(item.id),
        details=f"fields={','.join(sorted(updates.keys()))}",
    )
    db.commit()
    db.refresh(item)
    return MatchEventRead.model_validate(item)


@router.delete("/matches/{match_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match_event(
    match_id: int,
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    match = _get_match_or_404(db, match_id)
    _assert_match_editable(match, current_user)

    item = db.query(MatchEvent).filter(MatchEvent.id == event_id, MatchEvent.match_id == match_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match event not found")

    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="delete",
        entity="match_event",
        entity_id=str(item.id),
        details=f"match_id={match_id}",
    )
    db.delete(item)
    db.commit()
