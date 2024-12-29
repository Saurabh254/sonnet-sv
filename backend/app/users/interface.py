from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth
from app.exceptions import UnauthorisedUser

from . import errors, models, schemas


async def login_user(phone: str, otp: str, db: AsyncSession) -> dict[str, Any]:
    if phone[-6:] != otp:
        raise UnauthorisedUser
    stmt = select(models.User).where(models.User.phone == phone)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise errors.UserNotFound

    if not user.active:
        raise UnauthorisedUser

    access_token = auth.create_access_token(user=user)
    return {
        "access_token": access_token,
        "user": user.__dict__,
    }


async def signup_user(user_data: schemas.UserCreate, db: AsyncSession) -> models.User:
    is_existing_stmt = (
        select(func.count())
        .select_from(models.User)
        .filter(models.User.phone == user_data.phone)
    )
    result = await db.execute(is_existing_stmt)
    count = result.scalar()
    if count:
        raise errors.UserAlreadyExists

    user = models.User(**user_data.model_dump(exclude={"otp"}))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def logout_user(user: models.User) -> dict[str, str]:
    return {"msg": "Successfully logged out"}


async def get_user(user_id: str, db: AsyncSession) -> models.User:
    stmt = select(models.User).filter(models.User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
