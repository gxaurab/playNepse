from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password, require_role
from app.db import get_db
from app.errors import AppError
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(
    prefix="/api/admin/users",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("", response_model=list[UserOut])
def list_users(db: Annotated[Session, Depends(get_db)]) -> list[User]:
    users = db.execute(select(User).order_by(User.id)).scalars().all()
    return list(users)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing is not None:
        raise AppError(
            status=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message="User with this email already exists",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{id}", response_model=UserOut)
def update_user(
    id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.get(User, id)
    if user is None:
        raise AppError(
            status=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message="User not found",
        )

    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user
