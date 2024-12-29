from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.mixins import BaseModel
from app.drivers import models


class Vehicle(BaseModel):
    __tablename__ = "vehicle"

    license_number = Column(String(50), unique=True, nullable=False)
    registration_number = Column(String(100), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    driver = relationship("Driver", back_populates="driver", uselist=False)

    def __repr__(self):
        return f"<Vehicle(license_number={self.license_number}, driver_id={self.driver_id}, capacity={self.capacity})>"
