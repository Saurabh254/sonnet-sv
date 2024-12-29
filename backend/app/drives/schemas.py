from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.drivers.schemas import DriverProfile
from app.users.schemas import UserProfile
from app.vehicle.schemas import SlimVehicleProfile, VehicleProfile


class DriveStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"


class DriveCreate(BaseModel):
    driver_id: str
    vehicle_id: str
    pickup_location: "Location"  # You can define a more specific type if needed
    dropoff_location: "Location"  # Y


class Location(BaseModel):
    longitude: float
    latitude: float


class DriveUpdate(BaseModel):
    driver_id: Optional[str]
    pickup_location: Location  # You can define a more specific type if needed
    dropoff_location: Location  # You can define a more specific type if needed
    status: Optional[DriveStatus]  # Status can also be updated


class Driver(BaseModel):
    name: str
    id: str
    created_at: datetime
    updated_at: datetime


class SlimDrive(BaseModel):
    status: DriveStatus
    driver_id: str
    id: str
    user: UserProfile | None = None
    driver: DriverProfile | None = None
    created_at: datetime
    updated_at: datetime


class Drive(BaseModel):
    status: DriveStatus
    driver_id: str
    id: str
    user: UserProfile | None = None
    driver: DriverProfile | None = None
    pickup_location: Location | None = None
    dropoff_location: Location | None = None
    created_at: datetime
    updated_at: datetime
    vehicle: SlimVehicleProfile | None = None

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy models
