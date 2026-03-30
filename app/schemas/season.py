from pydantic import BaseModel, Field


class SeasonCreate(BaseModel):
    competition_id: int = Field(ge=1)
    label: str = Field(min_length=4, max_length=20)
    points_win: int = 3
    points_draw: int = 1
    points_loss: int = 0


class SeasonUpdate(BaseModel):
    competition_id: int | None = Field(default=None, ge=1)
    label: str | None = Field(default=None, min_length=4, max_length=20)
    points_win: int | None = None
    points_draw: int | None = None
    points_loss: int | None = None


class SeasonRead(BaseModel):
    id: int
    competition_id: int
    label: str
    points_win: int
    points_draw: int
    points_loss: int

    model_config = {"from_attributes": True}
