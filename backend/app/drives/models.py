import enum

from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship

from app.database.mixins import BaseModel


class DriveStatus(enum.Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"


class Drive(BaseModel):
    __tablename__ = "drives"  # Updated table name

    driver_id = Column(
        String, ForeignKey("drivers.id"), nullable=False
    )  # Assuming this is still valid
    user_id = Column(
        String, ForeignKey("users.id"), nullable=False
    )  # Assuming you have a User model
    pickup_location = Column(
        Geometry(geometry_type="POINT", srid=4326)
    )  # SRID 4326 is standard for GPS lat/lon
    dropoff_location = Column(
        Geometry(geometry_type="POINT", srid=4326)
    )  # SRID 4326 is standard for GPS lat/lon
    vehicle_id = Column(String, ForeignKey("vehicle.id"), nullable=False)
    status = Column(
        SQLAEnum(DriveStatus), nullable=False, default=DriveStatus.ACCEPTED
    )  # Default status

    # Relationship with the User model
    user = relationship("User", back_populates="drives")  # Updated relationship name
    driver = relationship("Driver")  # Updated relationship name
    vehicle = relationship("Vehicle")

    def __repr__(self):
        return f"<Drive(driver_id={self.driver_id}, status={self.status}, location={self.location})>"
