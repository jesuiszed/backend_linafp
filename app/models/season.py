from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint("competition_id", "label", name="uq_season_competition_label"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    points_win: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    points_draw: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    points_loss: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    competition = relationship("Competition", back_populates="seasons")
    memberships = relationship("SquadMembership", back_populates="season", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="season", cascade="all, delete-orphan")
