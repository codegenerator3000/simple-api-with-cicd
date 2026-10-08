from sqlalchemy import ForeignKey
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk


class Street(Base):
    __tablename__ = "streets"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(mysql.VARCHAR(255))
    city_id: Mapped[int] = mapped_column(mysql.INTEGER, ForeignKey("cities.id"))

    city: Mapped["City"] = relationship(back_populates="streets")
    markets: Mapped[list["Market"]] = relationship(back_populates="street")
