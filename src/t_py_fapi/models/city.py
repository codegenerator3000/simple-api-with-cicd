from pydantic import BaseModel


class CityDTO(BaseModel):
    id: int
    name: str
