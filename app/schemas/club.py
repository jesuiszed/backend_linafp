from pydantic import BaseModel, Field


class ClubCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    city: str | None = Field(default=None, max_length=80)
    stadium: str | None = Field(default=None, max_length=120)
    logo_url: str | None = Field(default=None, max_length=255)


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, max_length=80)
    stadium: str | None = Field(default=None, max_length=120)
    logo_url: str | None = Field(default=None, max_length=255)


class ClubRead(BaseModel):
    id: int
    name: str
    city: str | None
    stadium: str | None
    logo_url: str | None

    model_config = {"from_attributes": True}
