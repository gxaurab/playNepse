import enum
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class CrawlTrigger(str, enum.Enum):
    schedule = "schedule"
    manual = "manual"


class CrawlStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.viewer,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str | None] = mapped_column(String, nullable=True)
    aliases: Mapped[list[Any]] = mapped_column(
        JSONB,
        default=list,
        server_default="[]",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Price(Base):
    __tablename__ = "prices"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    high: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    low: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    close: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    turnover: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    trades: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    vwap: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)


class Floorsheet(Base):
    __tablename__ = "floorsheet"

    contract_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    business_date: Mapped[date] = mapped_column(Date, nullable=False)
    buyer_broker: Mapped[str | None] = mapped_column(String, nullable=True)
    seller_broker: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    trade_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    __table_args__ = (
        Index("ix_floorsheet_company_id_business_date", "company_id", "business_date"),
    )


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class NewsTag(Base):
    __tablename__ = "news_tags"

    news_id: Mapped[int] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"),
        primary_key=True,
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False)


class TagCorrection(Base):
    __tablename__ = "tag_corrections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    before: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class CrawlRun(Base):
    __tablename__ = "crawl_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    trigger: Mapped[CrawlTrigger] = mapped_column(
        Enum(CrawlTrigger, native_enum=False),
        nullable=False,
    )
    status: Mapped[CrawlStatus] = mapped_column(
        Enum(CrawlStatus, native_enum=False),
        default=CrawlStatus.queued,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    items_new: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
