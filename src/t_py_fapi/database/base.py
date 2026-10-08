from typing import Annotated

from sqlalchemy.dialects import mysql
from sqlalchemy.orm import DeclarativeBase, mapped_column


intpk = Annotated[int, mapped_column(mysql.INTEGER, primary_key=True)]


class Base(DeclarativeBase):
    pass
