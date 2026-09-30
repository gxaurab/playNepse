import json
import logging
from datetime import UTC, datetime
from typing import Any

import redis

from app.config import get_settings

logger = logging.getLogger(__name__)


def publish(event_type: str, payload: dict[str, Any]) -> None:
    settings = get_settings()
    data = {
        "type": event_type,
        **payload,
        "at": datetime.now(UTC).isoformat(),
    }
    msg = json.dumps(data)
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.publish("updates", msg)
    except redis.RedisError as exc:
        logger.warning("Failed publishing event %s: %s", event_type, exc)
