# Import all models here so Alembic can discover metadata.
from app.db.base_class import Base
from app.models.audit_log import AuditLog
from app.models.article import Article
from app.models.club import Club
from app.models.competition import Competition
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.player import Player
from app.models.season import Season
from app.models.squad_membership import SquadMembership
from app.models.user import User

__all__ = [
    "Base",
    "AuditLog",
    "Article",
    "Competition",
    "Season",
    "Club",
    "Player",
    "SquadMembership",
    "Match",
    "MatchEvent",
    "User",
]
