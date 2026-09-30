from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:helloworld@localhost:5432/playnepse"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str
    JWT_EXPIRE_MIN: int = 720

    SEED_ADMIN_EMAIL: str = "admin@playnepse.local"
    SEED_ADMIN_PASSWORD: str = "admin12345"
    SEED_ANALYST_EMAIL: str = "analyst@playnepse.local"
    SEED_ANALYST_PASSWORD: str = "analyst12345"
    SEED_VIEWER_EMAIL: str = "viewer@playnepse.local"
    SEED_VIEWER_PASSWORD: str = "viewer12345"

    COOKIE_SECURE: bool = False
    COOKIE_NAME: str = "access_token"

    COMPANIES_FILE: str = "../config/companies.yaml"

    model_config = SettingsConfigDict(
        env_file=(_BASE_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
