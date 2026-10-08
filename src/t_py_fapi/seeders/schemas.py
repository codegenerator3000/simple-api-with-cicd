from pydantic import BaseModel


class CitySeed(BaseModel):
    name: str


class StreetSeed(BaseModel):
    name: str
    city: str


class SeedData(BaseModel):
    cities: list[CitySeed]
    streets: list[StreetSeed]
