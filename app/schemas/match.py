from datetime import datetime

from pydantic import BaseModel, Field

from app.models.match import MatchStatus


class MatchCreate(BaseModel):
    season_id: int = Field(ge=1)
    matchday: int = Field(ge=1)
    kickoff_at: datetime
    stadium: str | None = Field(default=None, max_length=120)
    club_home_id: int = Field(ge=1)
    club_away_id: int = Field(ge=1)
    status: MatchStatus = MatchStatus.SCHEDULED


class MatchUpdate(BaseModel):
    season_id: int | None = Field(default=None, ge=1)
    matchday: int | None = Field(default=None, ge=1)
    kickoff_at: datetime | None = None
    stadium: str | None = Field(default=None, max_length=120)
    club_home_id: int | None = Field(default=None, ge=1)
    club_away_id: int | None = Field(default=None, ge=1)
    status: MatchStatus | None = None


class MatchScoreUpdate(BaseModel):
    home_score_ht: int = Field(ge=0)
    away_score_ht: int = Field(ge=0)
    home_score_ft: int = Field(ge=0)
    away_score_ft: int = Field(ge=0)


class MatchRead(BaseModel):
    id: int
    season_id: int
    matchday: int
    kickoff_at: datetime
    stadium: str | None
    club_home_id: int
    club_away_id: int
    status: MatchStatus
    is_locked: bool
    home_score_ht: int
    away_score_ht: int
    home_score_ft: int
    away_score_ft: int

    model_config = {"from_attributes": True}
