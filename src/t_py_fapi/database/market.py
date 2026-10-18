from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk

if TYPE_CHECKING:
    from .street import Street


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    street_id: Mapped[int] = mapped_column(Integer, ForeignKey("streets.id"))
    house_number: Mapped[str] = mapped_column(String(255))
    opening_time: Mapped[time] = mapped_column(Time)
    closing_time: Mapped[time] = mapped_column(Time)

    street: Mapped[Street] = relationship(back_populates="markets")
