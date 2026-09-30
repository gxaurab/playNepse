from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.config import get_settings
from app.db import get_db
from app.errors import AppError
from app.models import User
from app.schemas import LoginIn, StatusResponse, Token, UserOut

settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(
    payload: LoginIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(status=401, code="UNAUTHORIZED", message="Invalid email or password")

    if not user.is_active:
        raise AppError(status=401, code="UNAUTHORIZED", message="User account is inactive")

    token = create_access_token(user)
    max_age = settings.JWT_EXPIRE_MIN * 60

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
    )
    return user


@router.post("/logout", response_model=StatusResponse)
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
    )
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.post("/token", response_model=Token)
def token_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    user = db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()
    if (
        user is None
        or not verify_password(form_data.password, user.password_hash)
        or not user.is_active
    ):
        raise AppError(status=401, code="UNAUTHORIZED", message="Invalid email or password")

    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer"}
