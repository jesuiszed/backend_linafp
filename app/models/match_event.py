from enum import Enum

from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MatchEventType(str, Enum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"


class MatchEvent(Base):
    __tablename__ = "match_events"
    __table_args__ = (
        CheckConstraint('minute >= 0 AND minute <= 130', name='ck_match_event_minute_range'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="RESTRICT"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"), nullable=False)
    related_player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"), nullable=True)
    event_type: Mapped[MatchEventType] = mapped_column(SqlEnum(MatchEventType), nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)

    match = relationship("Match", back_populates="events")
