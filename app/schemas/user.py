from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole


class UserMe(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BootstrapAdminRequest(BaseModel):
    username: str
    password: str
