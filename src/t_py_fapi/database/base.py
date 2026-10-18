from typing import Annotated

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column

intpk = Annotated[int, mapped_column(Integer, primary_key=True)]


class Base(DeclarativeBase):
    pass
