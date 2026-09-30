from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.events import publish
from app.models import CrawlRun, CrawlStatus, CrawlTrigger


@contextmanager
def track_run(
    db: Session,
    job_type: str,
    source: str,
    trigger: str | CrawlTrigger = "manual",
) -> Generator[CrawlRun, None, None]:
    trigger_val = trigger if isinstance(trigger, CrawlTrigger) else CrawlTrigger(trigger)
    run = CrawlRun(
        job_type=job_type,
        source=source,
        trigger=trigger_val,
        status=CrawlStatus.running,
        started_at=datetime.now(UTC),
        items_new=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        yield run
        run.status = CrawlStatus.success
    except Exception as exc:
        run.status = CrawlStatus.failed
        run.error = str(exc)[:2000]
        raise
    finally:
        run.finished_at = datetime.now(UTC)
        db.commit()
        status_val = run.status.value if hasattr(run.status, "value") else str(run.status)
        publish("crawl_run", {"id": run.id, "job_type": run.job_type, "status": status_val})
