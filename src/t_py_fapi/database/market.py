from datetime import time

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, intpk


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(mysql.VARCHAR(255))
    street_id: Mapped[int] = mapped_column(mysql.INTEGER, ForeignKey("streets.id"))
    house_number: Mapped[str] = mapped_column(mysql.VARCHAR(255))
    opening_time: Mapped[time] = mapped_column(mysql.TIME)
    closing_time: Mapped[time] = mapped_column(mysql.TIME)

    street: Mapped["Street"] = relationship(back_populates="markets")
