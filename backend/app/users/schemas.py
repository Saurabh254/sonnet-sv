from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    phone: str
    otp: str


class UserProfile(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Allows Pydantic to read data from ORM models


class LoginResponse(BaseModel):
    access_token: str
    user: UserProfile
