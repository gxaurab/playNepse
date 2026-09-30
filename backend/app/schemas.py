from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.models import CrawlStatus, CrawlTrigger, UserRole


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


class CompanyOut(BaseModel):
    id: int
    symbol: str
    name: str
    sector: str | None
    aliases: list[Any]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    symbol: str
    name: str
    sector: str | None = None
    aliases: list[str] = []
    is_active: bool = True


class CompanyUpdate(BaseModel):
    name: str | None = None
    sector: str | None = None
    aliases: list[str] | None = None
    is_active: bool | None = None


class PriceOut(BaseModel):
    company_id: int
    date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: Decimal | None
    turnover: Decimal | None
    trades: Decimal | None
    vwap: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class CrawlRunOut(BaseModel):
    id: int
    job_type: str
    source: str
    trigger: CrawlTrigger
    status: CrawlStatus
    started_at: datetime | None
    finished_at: datetime | None
    items_new: int
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class CrawlRunEnqueueIn(BaseModel):
    job: Literal["prices", "floorsheet"]
    days: int | None = None


class CrawlRunEnqueueOut(BaseModel):
    task_id: str
    job: str
