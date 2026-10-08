from datetime import time

from pydantic import BaseModel

from .street import StreetDTO


class MarketDTO(BaseModel):
    id: int
    name: str
    street: StreetDTO
    home_address: str
    opening_time: time
    closing_time: time
