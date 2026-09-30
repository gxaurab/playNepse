import asyncio

import jwt
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.db import SessionLocal
from app.models import User

router = APIRouter(tags=["websocket"])
settings = get_settings()


@router.websocket("/ws/updates")
async def ws_updates(websocket: WebSocket) -> None:
    token = websocket.cookies.get(settings.COOKIE_NAME)
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            await websocket.close(code=1008)
            return
        user_id = int(user_id_raw)
    except (jwt.PyJWTError, ValueError):
        await websocket.close(code=1008)
        return

    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None or not user.is_active:
            await websocket.close(code=1008)
            return

    await websocket.accept()

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("updates")

    async def forward_updates() -> None:
        async for message in pubsub.listen():
            if message.get("type") == "message":
                data = message.get("data")
                if data is not None:
                    await websocket.send_text(str(data))

    async def receive_pings() -> None:
        while True:
            await websocket.receive_text()

    try:
        await asyncio.gather(forward_updates(), receive_pings())
    except (WebSocketDisconnect, ConnectionResetError, asyncio.CancelledError):
        pass
    finally:
        await pubsub.unsubscribe("updates")
        await pubsub.close()
        await redis_client.aclose()
