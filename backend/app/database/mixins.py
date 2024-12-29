import datetime

from nanoid import generate
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import \
    Base  # Assuming you have a Base class defined in your db module


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, default=lambda: generate(size=12)
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True,
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    def as_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_
