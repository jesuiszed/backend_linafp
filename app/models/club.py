from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    stadium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    memberships = relationship("SquadMembership", back_populates="club", cascade="all, delete-orphan")
    home_matches = relationship(
        "Match",
        back_populates="home_club",
        foreign_keys="Match.club_home_id",
    )
    away_matches = relationship(
        "Match",
        back_populates="away_club",
        foreign_keys="Match.club_away_id",
    )
