from __future__ import annotations

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from app.config import get_settings

settings = get_settings()

app = Celery(
    "playnepse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    timezone="Asia/Kathmandu",
    include=["app.tasks"],
)

app.conf.task_default_queue = "default"
app.conf.task_queues = (
    Queue("default"),
    Queue("market"),
)

app.conf.task_routes = {
    "app.tasks.market.*": {"queue": "market"},
}

app.conf.beat_schedule = {
    "backfill-prices-schedule": {
        "task": "app.tasks.market.backfill_prices",
        "schedule": crontab(hour=15, minute=20, day_of_week="sun-thu"),
        "args": (5, "schedule"),
    },
    "fetch-floorsheet-schedule": {
        "task": "app.tasks.market.fetch_floorsheet",
        "schedule": crontab(hour=15, minute=25, day_of_week="sun-thu"),
        "args": ("schedule",),
    },
}