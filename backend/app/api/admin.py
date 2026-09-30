from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import CrawlRun
from app.schemas import CrawlRunEnqueueIn, CrawlRunEnqueueOut, CrawlRunOut
from app.tasks.market import backfill_prices, fetch_floorsheet

router = APIRouter(
    prefix="/api/admin/crawl-runs",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)


@router.post("", response_model=CrawlRunEnqueueOut, status_code=status.HTTP_202_ACCEPTED)
def enqueue_crawl_run(payload: CrawlRunEnqueueIn) -> CrawlRunEnqueueOut:
    if payload.job == "prices":
        days = payload.days if payload.days is not None else 5
        task = backfill_prices.delay(days=days, trigger="manual")
    else:
        task = fetch_floorsheet.delay(trigger="manual")

    return CrawlRunEnqueueOut(task_id=task.id, job=payload.job)


@router.get("", response_model=list[CrawlRunOut])
def list_crawl_runs(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CrawlRun]:
    runs = db.execute(select(CrawlRun).order_by(CrawlRun.id.desc()).limit(limit)).scalars().all()
    return list(runs)
