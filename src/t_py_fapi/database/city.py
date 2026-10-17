from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk

if TYPE_CHECKING:
    from .street import Street


class City(Base):
    __tablename__ = "cities"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))

    streets: Mapped[list[Street]] = relationship(back_populates="city")
