from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk


class Street(Base):
    __tablename__ = "streets"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"))

    city: Mapped["City"] = relationship(back_populates="streets")
    markets: Mapped[list["Market"]] = relationship(back_populates="street")
