from typing import Dict, Optional

from geoalchemy2.elements import WKBElement
from pydantic import BaseModel, Field
from shapely import wkb
from sqlalchemy.orm import Session

from app.drivers import schemas as driver_schemas


class VehicleBase(BaseModel):
    license_number: str
    registration_number: str
    capacity: int


class VehicleCreate(VehicleBase): ...


class VehicleUpdate(BaseModel):
    license_number: Optional[str] = None
    registration_number: Optional[str] = None
    capacity: Optional[int] = None


# Helper function to convert location data to lat/lng
def extract_coordinates(location: WKBElement) -> Dict[str, float]:
    if location:
        point = wkb.loads(bytes(location.data))  # Use shapely to load the WKB data
        return {
            "latitude": point.y,
            "longitude": point.x,
        }  # Extract lat (y) and long (x)
    return {"latitude": None, "longitude": None}


class SlimVehicleProfile(BaseModel):
    id: str
    license_number: str
    registration_number: str
    capacity: int
    driver_id: str
    location: Dict[str, float]


class VehicleProfile(SlimVehicleProfile):
    driver: driver_schemas.DriverProfile

    @classmethod
    def from_orm(cls, vehicle: "Vehicle"):
        return cls(
            id=vehicle.id,
            license_number=vehicle.license_number,
            registration_number=vehicle.registration_number,
            capacity=vehicle.capacity,
            driver=vehicle.driver.__dict__,
            driver_id=str(vehicle.driver_id),
            location=extract_coordinates(
                vehicle.location
            ),  # Convert location to lat/long dict
        )

    class Config:
        orm_mode = True
