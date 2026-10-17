from pydantic import BaseModel, ConfigDict

from .city import CityDTO


class StreetDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: CityDTO
