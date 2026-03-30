from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent, MatchEventType
from app.models.player import Player
from app.models.user import UserRole

router = APIRouter()


@router.get("/inconsistencies")
def get_inconsistencies(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> dict:
    issues: list[dict] = []

    duplicate_players = (
        db.query(Player.first_name, Player.last_name, Player.birth_date, func.count(Player.id).label("cnt"))
        .group_by(Player.first_name, Player.last_name, Player.birth_date)
        .having(func.count(Player.id) > 1)
        .all()
    )
    for row in duplicate_players:
        issues.append(
            {
                "type": "duplicate_player",
                "severity": "warning",
                "message": f"Possible duplicate player: {row.first_name} {row.last_name}",
                "details": {"birth_date": str(row.birth_date), "count": row.cnt},
            }
        )

    duplicate_matches = (
        db.query(
            Match.season_id,
            Match.matchday,
            Match.club_home_id,
            Match.club_away_id,
            func.count(Match.id).label("cnt"),
        )
        .group_by(Match.season_id, Match.matchday, Match.club_home_id, Match.club_away_id)
        .having(func.count(Match.id) > 1)
        .all()
    )
    for row in duplicate_matches:
        issues.append(
            {
                "type": "duplicate_match",
                "severity": "error",
                "message": "Duplicate match scheduling detected",
                "details": {
                    "season_id": row.season_id,
                    "matchday": row.matchday,
                    "club_home_id": row.club_home_id,
                    "club_away_id": row.club_away_id,
                    "count": row.cnt,
                },
            }
        )

    finished_locked_matches = (
        db.query(Match)
        .filter(Match.status == MatchStatus.FINISHED, Match.is_locked.is_(True))
        .all()
    )
    match_ids = [m.id for m in finished_locked_matches]

    events = (
        db.query(MatchEvent)
        .filter(MatchEvent.match_id.in_(match_ids), MatchEvent.event_type == MatchEventType.GOAL)
        .all()
        if match_ids
        else []
    )

    goals_by_match_team: dict[tuple[int, int], int] = defaultdict(int)
    for event in events:
        goals_by_match_team[(event.match_id, event.team_id)] += 1

    for match in finished_locked_matches:
        home_goals = goals_by_match_team.get((match.id, match.club_home_id), 0)
        away_goals = goals_by_match_team.get((match.id, match.club_away_id), 0)
        if home_goals > match.home_score_ft or away_goals > match.away_score_ft:
            issues.append(
                {
                    "type": "goals_exceed_score",
                    "severity": "error",
                    "message": "Goal events exceed stored final score",
                    "details": {
                        "match_id": match.id,
                        "score_home_ft": match.home_score_ft,
                        "score_away_ft": match.away_score_ft,
                        "goal_events_home": home_goals,
                        "goal_events_away": away_goals,
                    },
                }
            )

    return {"data": issues, "meta": {"count": len(issues)}}
