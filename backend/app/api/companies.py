from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role
from app.db import get_db
from app.errors import AppError
from app.models import Company, Price, User
from app.schemas import CompanyCreate, CompanyOut, CompanyUpdate, PriceOut

router = APIRouter(prefix="/api/companies", tags=["companies"])

RANGE_MAP = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
}


@router.get("", response_model=list[CompanyOut])
def list_companies(
    _current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Company]:
    companies = db.execute(select(Company).order_by(Company.symbol)).scalars().all()
    return list(companies)


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    _admin_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> Company:
    existing = db.execute(
        select(Company).where(Company.symbol == payload.symbol)
    ).scalar_one_or_none()
    if existing is not None:
        raise AppError(status.HTTP_409_CONFLICT, "CONFLICT", "Company symbol already exists")

    company = Company(
        symbol=payload.symbol,
        name=payload.name,
        sector=payload.sector,
        aliases=payload.aliases,
        is_active=payload.is_active,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.patch("/{id}", response_model=CompanyOut)
def update_company(
    id: int,
    payload: CompanyUpdate,
    _admin_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> Company:
    company = db.get(Company, id)
    if company is None:
        raise AppError(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Company not found")

    if payload.name is not None:
        company.name = payload.name
    if payload.sector is not None:
        company.sector = payload.sector
    if payload.aliases is not None:
        company.aliases = payload.aliases
    if payload.is_active is not None:
        company.is_active = payload.is_active

    db.commit()
    db.refresh(company)
    return company


@router.get("/{id}/prices", response_model=list[PriceOut])
def get_company_prices(
    id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    range: Literal["7d", "30d", "90d"] = Query(default="30d"),
) -> list[Price]:
    company = db.get(Company, id)
    if company is None:
        raise AppError(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Company not found")

    days = RANGE_MAP[range]
    cutoff_date = (datetime.now(UTC) - timedelta(days=days)).date()

    prices = (
        db.execute(
            select(Price)
            .where(Price.company_id == id, Price.date >= cutoff_date)
            .order_by(Price.date.asc())
        )
        .scalars()
        .all()
    )
    return list(prices)
