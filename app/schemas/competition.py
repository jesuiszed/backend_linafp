from pydantic import BaseModel, Field


class CompetitionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    is_archived: bool = False


class CompetitionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    is_archived: bool | None = None


class CompetitionRead(BaseModel):
    id: int
    name: str
    is_archived: bool

    model_config = {"from_attributes": True}
