from sqlalchemy import select

from app.auth import hash_password
from app.config import get_settings
from app.db import SessionLocal
from app.models import User, UserRole


def seed_users() -> None:
    settings = get_settings()
    seed_data = [
        (settings.SEED_ADMIN_EMAIL, settings.SEED_ADMIN_PASSWORD, UserRole.admin),
        (settings.SEED_ANALYST_EMAIL, settings.SEED_ANALYST_PASSWORD, UserRole.analyst),
        (settings.SEED_VIEWER_EMAIL, settings.SEED_VIEWER_PASSWORD, UserRole.viewer),
    ]

    with SessionLocal() as db:
        for email, password, role in seed_data:
            existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if existing is None:
                user = User(
                    email=email,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
                db.add(user)
        db.commit()
