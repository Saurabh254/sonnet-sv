from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.mixins import BaseModel
from app.vehicle import models


class Driver(BaseModel):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)

    driver = relationship("Vehicle", back_populates="driver", uselist=False)

    def __repr__(self):
        return f"<Driver(name='{self.name}')>"
