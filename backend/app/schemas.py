from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole


class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StatusResponse(BaseModel):
    status: str = "ok"
