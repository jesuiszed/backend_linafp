from pydantic import BaseModel, Field

from app.models.match_event import MatchEventType


class MatchEventCreate(BaseModel):
    team_id: int = Field(ge=1)
    player_id: int = Field(ge=1)
    related_player_id: int | None = Field(default=None, ge=1)
    event_type: MatchEventType
    minute: int = Field(ge=0, le=130)


class MatchEventUpdate(BaseModel):
    team_id: int | None = Field(default=None, ge=1)
    player_id: int | None = Field(default=None, ge=1)
    related_player_id: int | None = Field(default=None, ge=1)
    event_type: MatchEventType | None = None
    minute: int | None = Field(default=None, ge=0, le=130)


class MatchEventRead(BaseModel):
    id: int
    match_id: int
    team_id: int
    player_id: int
    related_player_id: int | None
    event_type: MatchEventType
    minute: int

    model_config = {"from_attributes": True}
