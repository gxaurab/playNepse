import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.db import init_db
from app.errors import register_error_handlers
from app.seed import seed_users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    seed_users()
    yield


app = FastAPI(
    title="playNepse API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}
