from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk

if TYPE_CHECKING:
    from .city import City
    from .market import Market


class Street(Base):
    __tablename__ = "streets"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"))

    city: Mapped[City] = relationship(back_populates="streets")
    markets: Mapped[list[Market]] = relationship(back_populates="street")
