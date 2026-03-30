from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class PaginatedMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: list[str] = []
