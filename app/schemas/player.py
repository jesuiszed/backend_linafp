from datetime import date

from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    birth_date: date | None = None
    nationality: str | None = Field(default=None, max_length=60)
    position: str | None = Field(default=None, max_length=40)


class PlayerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    birth_date: date | None = None
    nationality: str | None = Field(default=None, max_length=60)
    position: str | None = Field(default=None, max_length=40)


class PlayerRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: date | None
    nationality: str | None
    position: str | None

    model_config = {"from_attributes": True}
