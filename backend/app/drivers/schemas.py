from datetime import datetime

from pydantic import BaseModel


class DriverBase(BaseModel):
    name: str


class DriverCreate(DriverBase):
    phone: str
    otp: str


class DriverProfile(DriverBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LoginResponse(BaseModel):
    access_token: str
    driver: DriverProfile
