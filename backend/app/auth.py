from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.errors import AppError
from app.models import User, UserRole

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user: User) -> str:
    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MIN)
    payload = {
        "sub": str(user.id),
        "role": role_val,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(
    request: Request,
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    token = request.cookies.get(settings.COOKIE_NAME) or bearer_token
    if not token:
        raise AppError(
            status=401,
            code="UNAUTHORIZED",
            message="Authentication credentials were not provided",
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise AppError(status=401, code="UNAUTHORIZED", message="Invalid authentication token")
        user_id = int(user_id_raw)
    except (jwt.PyJWTError, ValueError):
        raise AppError(
            status=401,
            code="UNAUTHORIZED",
            message="Invalid or expired authentication token",
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(status=401, code="UNAUTHORIZED", message="User inactive or not found")

    return user


def require_role(*roles: str | UserRole) -> Callable[..., User]:
    allowed = {r.value if hasattr(r, "value") else str(r) for r in roles}

    def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        user_role = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        )
        if user_role not in allowed:
            raise AppError(status=403, code="FORBIDDEN", message="Permission denied")
        return current_user

    return role_dependency
