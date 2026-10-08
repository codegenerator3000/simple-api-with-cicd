from pydantic import BaseModel

from .city import CityDTO


class StreetDTO(BaseModel):
    id: int
    name: str
    city: CityDTO
