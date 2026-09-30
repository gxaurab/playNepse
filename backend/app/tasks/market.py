from app.celery_app import app
from app.services.market import backfill_prices as svc_backfill_prices
from app.services.market import fetch_floorsheet as svc_fetch_floorsheet


@app.task(
    queue="market",
    rate_limit="10/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def backfill_prices(days: int = 5, trigger: str = "manual") -> int:
    return svc_backfill_prices(days=days, trigger=trigger)


@app.task(
    queue="market",
    rate_limit="10/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def fetch_floorsheet(trigger: str = "manual") -> int:
    return svc_fetch_floorsheet(trigger=trigger)
