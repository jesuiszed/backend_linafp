from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELED = "canceled"


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("season_id", "matchday", "club_home_id", "club_away_id", name="uq_match_schedule"),
        CheckConstraint("club_home_id <> club_away_id", name="ck_match_distinct_clubs"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    matchday: Mapped[int] = mapped_column(Integer, nullable=False)
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stadium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    club_home_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="RESTRICT"), nullable=False)
    club_away_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[MatchStatus] = mapped_column(SqlEnum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False)
    is_locked: Mapped[bool] = mapped_column(default=False, nullable=False)
    home_score_ht: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_score_ht: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    home_score_ft: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_score_ft: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    season = relationship("Season", back_populates="matches")
    home_club = relationship("Club", foreign_keys=[club_home_id], back_populates="home_matches")
    away_club = relationship("Club", foreign_keys=[club_away_id], back_populates="away_matches")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
