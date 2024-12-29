from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth
from app.database.db import get_async_db

from . import interface, models, schemas

router = APIRouter(tags=["User Authentication"], prefix="/users")


@router.post(
    "/login",
    description="Log in the user with a phone number and OTP to get an access token.",
    response_model=schemas.LoginResponse,
)
async def login(
    phone: str = Body(..., description="User's phone number"),
    otp: str = Body(..., description="One-time password sent to the user's phone"),
    db: AsyncSession = Depends(get_async_db),
):
    return await interface.login_user(phone, otp, db)


@router.post(
    "/signup",
    description="Sign up a new user using the provided data.",
    response_model=schemas.UserProfile,
)
async def signup(
    user_data: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)
):
    return await interface.signup_user(user_data=user_data, db=db)


@router.post(
    "/logout",
    description="Logs out the currently authenticated user and invalidates the session.",
    response_model=schemas.UserProfile,
)
async def logout(current_user: models.User = Depends(auth.get_current_active_user)):
    return await interface.logout_user(current_user)


@router.get(
    "/me",
    response_model=schemas.UserProfile,
    description="Retrieve the profile of the currently authenticated user.",
)
async def read_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user
