from fastapi import APIRouter

from app.api.v1.endpoints import articles, audit_logs, auth, clubs, competitions, health, match_events, matches, players, quality, seasons, standings, stats

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(seasons.router, prefix="/seasons", tags=["seasons"])
api_router.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(match_events.router, tags=["match-events"])
api_router.include_router(standings.router, prefix="/standings", tags=["standings"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
