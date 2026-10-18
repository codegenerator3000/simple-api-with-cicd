from datetime import time

from pydantic import BaseModel, ConfigDict

from .street import StreetDTO


class MarketDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    street: StreetDTO
    house_number: str
    opening_time: time
    closing_time: time


class MarketCreate(BaseModel):
    name: str
    street_id: int
    house_number: str
    opening_time: time
    closing_time: time
