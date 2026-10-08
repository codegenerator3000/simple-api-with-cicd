from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk


class City(Base):
    __tablename__ = "cities"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(mysql.VARCHAR(255))

    streets: Mapped[list["Street"]] = relationship(back_populates="city")
