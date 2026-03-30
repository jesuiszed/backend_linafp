from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.club import Club
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent, MatchEventType
from app.models.player import Player


def _season_finished_matches(db: Session, season_id: int) -> list[Match]:
    return (
        db.query(Match)
        .filter(Match.season_id == season_id, Match.status == MatchStatus.FINISHED, Match.is_locked.is_(True))
        .order_by(Match.kickoff_at.asc())
        .all()
    )


def _build_base_rows(db: Session, season_id: int) -> dict[int, dict]:
    clubs = db.query(Club).order_by(Club.name.asc()).all()
    rows = {}
    for club in clubs:
        rows[club.id] = {
            "club_id": club.id,
            "club_name": club.name,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
            "head_to_head_points": 0,
            "head_to_head_goal_difference": 0,
            "fair_play_score": 0,
            "season_id": season_id,
        }
    return rows


def _apply_match_result(rows: dict[int, dict], match: Match) -> None:
    home = rows.get(match.club_home_id)
    away = rows.get(match.club_away_id)
    if not home or not away:
        return

    home["played"] += 1
    away["played"] += 1

    home["goals_for"] += match.home_score_ft
    home["goals_against"] += match.away_score_ft
    away["goals_for"] += match.away_score_ft
    away["goals_against"] += match.home_score_ft

    if match.home_score_ft > match.away_score_ft:
        home["wins"] += 1
        away["losses"] += 1
        home["points"] += 3
    elif match.home_score_ft < match.away_score_ft:
        away["wins"] += 1
        home["losses"] += 1
        away["points"] += 3
    else:
        home["draws"] += 1
        away["draws"] += 1
        home["points"] += 1
        away["points"] += 1


def _apply_fair_play(rows: dict[int, dict], events: list[MatchEvent]) -> None:
    for event in events:
        if event.team_id not in rows:
            continue
        if event.event_type == MatchEventType.YELLOW_CARD:
            rows[event.team_id]["fair_play_score"] -= 1
        elif event.event_type == MatchEventType.RED_CARD:
            rows[event.team_id]["fair_play_score"] -= 4


def _compute_head_to_head(rows: dict[int, dict], matches: list[Match]) -> None:
    grouped: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    for row in rows.values():
        key = (row["points"], row["goal_difference"], row["goals_for"])
        grouped[key].append(row["club_id"])

    for _, club_ids in grouped.items():
        if len(club_ids) < 2:
            continue

        in_group = set(club_ids)
        for match in matches:
            if match.club_home_id not in in_group or match.club_away_id not in in_group:
                continue

            home = rows[match.club_home_id]
            away = rows[match.club_away_id]
            home_diff = match.home_score_ft - match.away_score_ft
            away_diff = -home_diff

            home["head_to_head_goal_difference"] += home_diff
            away["head_to_head_goal_difference"] += away_diff

            if match.home_score_ft > match.away_score_ft:
                home["head_to_head_points"] += 3
            elif match.home_score_ft < match.away_score_ft:
                away["head_to_head_points"] += 3
            else:
                home["head_to_head_points"] += 1
                away["head_to_head_points"] += 1


def compute_standings(db: Session, season_id: int) -> list[dict]:
    matches = _season_finished_matches(db, season_id)
    rows = _build_base_rows(db, season_id)

    for match in matches:
        _apply_match_result(rows, match)

    for row in rows.values():
        row["goal_difference"] = row["goals_for"] - row["goals_against"]

    match_ids = [m.id for m in matches]
    events = db.query(MatchEvent).filter(MatchEvent.match_id.in_(match_ids)).all() if match_ids else []
    _apply_fair_play(rows, events)
    _compute_head_to_head(rows, matches)

    ordered = sorted(
        rows.values(),
        key=lambda r: (
            -r["points"],
            -r["goal_difference"],
            -r["goals_for"],
            -r["head_to_head_points"],
            -r["head_to_head_goal_difference"],
            -r["fair_play_score"],
            r["club_name"].lower(),
        ),
    )

    for idx, row in enumerate(ordered, start=1):
        row["position"] = idx

    return ordered


def top_scorers(db: Session, season_id: int, limit: int) -> list[dict]:
    matches = _season_finished_matches(db, season_id)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return []

    events = (
        db.query(MatchEvent)
        .filter(MatchEvent.match_id.in_(match_ids), MatchEvent.event_type == MatchEventType.GOAL)
        .all()
    )

    goals_by_player: dict[int, int] = defaultdict(int)
    for event in events:
        goals_by_player[event.player_id] += 1

    if not goals_by_player:
        return []

    players = db.query(Player).filter(Player.id.in_(list(goals_by_player.keys()))).all()
    by_id = {p.id: p for p in players}

    rows = []
    for player_id, goals in goals_by_player.items():
        p = by_id.get(player_id)
        if not p:
            continue
        rows.append(
            {
                "player_id": player_id,
                "player_name": f"{p.first_name} {p.last_name}".strip(),
                "goals": goals,
            }
        )

    rows.sort(key=lambda x: (-x["goals"], x["player_name"].lower()))
    return rows[:limit]


def top_assists(db: Session, season_id: int, limit: int) -> list[dict]:
    matches = _season_finished_matches(db, season_id)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return []

    events = (
        db.query(MatchEvent)
        .filter(
            MatchEvent.match_id.in_(match_ids),
            MatchEvent.event_type == MatchEventType.GOAL,
            MatchEvent.related_player_id.is_not(None),
        )
        .all()
    )

    assists_by_player: dict[int, int] = defaultdict(int)
    for event in events:
        if event.related_player_id:
            assists_by_player[event.related_player_id] += 1

    if not assists_by_player:
        return []

    players = db.query(Player).filter(Player.id.in_(list(assists_by_player.keys()))).all()
    by_id = {p.id: p for p in players}

    rows = []
    for player_id, assists in assists_by_player.items():
        p = by_id.get(player_id)
        if not p:
            continue
        rows.append(
            {
                "player_id": player_id,
                "player_name": f"{p.first_name} {p.last_name}".strip(),
                "assists": assists,
            }
        )

    rows.sort(key=lambda x: (-x["assists"], x["player_name"].lower()))
    return rows[:limit]


def card_stats(db: Session, season_id: int) -> dict:
    matches = _season_finished_matches(db, season_id)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return {"by_club": [], "by_player": []}

    events = (
        db.query(MatchEvent)
        .filter(MatchEvent.match_id.in_(match_ids), MatchEvent.event_type.in_([MatchEventType.YELLOW_CARD, MatchEventType.RED_CARD]))
        .all()
    )

    club_counts: dict[int, dict] = defaultdict(lambda: {"yellow_cards": 0, "red_cards": 0})
    player_counts: dict[int, dict] = defaultdict(lambda: {"yellow_cards": 0, "red_cards": 0})

    for event in events:
        if event.event_type == MatchEventType.YELLOW_CARD:
            club_counts[event.team_id]["yellow_cards"] += 1
            player_counts[event.player_id]["yellow_cards"] += 1
        elif event.event_type == MatchEventType.RED_CARD:
            club_counts[event.team_id]["red_cards"] += 1
            player_counts[event.player_id]["red_cards"] += 1

    clubs = db.query(Club).filter(Club.id.in_(list(club_counts.keys()))).all() if club_counts else []
    players = db.query(Player).filter(Player.id.in_(list(player_counts.keys()))).all() if player_counts else []

    club_rows = []
    for club in clubs:
        counts = club_counts[club.id]
        club_rows.append(
            {
                "club_id": club.id,
                "club_name": club.name,
                "yellow_cards": counts["yellow_cards"],
                "red_cards": counts["red_cards"],
                "total_cards": counts["yellow_cards"] + counts["red_cards"],
            }
        )

    player_rows = []
    for player in players:
        counts = player_counts[player.id]
        player_rows.append(
            {
                "player_id": player.id,
                "player_name": f"{player.first_name} {player.last_name}".strip(),
                "yellow_cards": counts["yellow_cards"],
                "red_cards": counts["red_cards"],
                "total_cards": counts["yellow_cards"] + counts["red_cards"],
            }
        )

    club_rows.sort(key=lambda x: (-x["total_cards"], x["club_name"].lower()))
    player_rows.sort(key=lambda x: (-x["total_cards"], x["player_name"].lower()))

    return {"by_club": club_rows, "by_player": player_rows}


def club_form(db: Session, season_id: int, club_id: int, last: int) -> dict:
    matches = _season_finished_matches(db, season_id)
    filtered = [m for m in matches if club_id in {m.club_home_id, m.club_away_id}]
    recent = filtered[-last:] if last > 0 else filtered

    form = []
    for match in recent:
        if match.club_home_id == club_id:
            gf, ga = match.home_score_ft, match.away_score_ft
        else:
            gf, ga = match.away_score_ft, match.home_score_ft

        if gf > ga:
            result = "W"
        elif gf < ga:
            result = "L"
        else:
            result = "D"

        form.append(
            {
                "match_id": match.id,
                "result": result,
                "goals_for": gf,
                "goals_against": ga,
            }
        )

    return {"club_id": club_id, "season_id": season_id, "last": last, "form": form}


def player_summary(db: Session, season_id: int, player_id: int) -> dict:
    matches = _season_finished_matches(db, season_id)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return {"player_id": player_id, "season_id": season_id, "goals": 0, "assists": 0, "yellow_cards": 0, "red_cards": 0, "involved_matches": 0}

    events = db.query(MatchEvent).filter(MatchEvent.match_id.in_(match_ids)).all()

    goals = 0
    assists = 0
    yellow = 0
    red = 0
    involved_matches: set[int] = set()

    for event in events:
        if event.player_id == player_id:
            involved_matches.add(event.match_id)
            if event.event_type == MatchEventType.GOAL:
                goals += 1
            elif event.event_type == MatchEventType.YELLOW_CARD:
                yellow += 1
            elif event.event_type == MatchEventType.RED_CARD:
                red += 1

        if event.related_player_id == player_id and event.event_type == MatchEventType.GOAL:
            assists += 1
            involved_matches.add(event.match_id)

    return {
        "player_id": player_id,
        "season_id": season_id,
        "goals": goals,
        "assists": assists,
        "yellow_cards": yellow,
        "red_cards": red,
        "involved_matches": len(involved_matches),
    }
