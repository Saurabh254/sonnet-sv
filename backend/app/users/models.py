from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.mixins import BaseModel
from app.drives import models


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    drives = relationship("Drive", back_populates="user")

    def __repr__(self):
        return f"<User(name='{self.name}', active={self.active})>"
