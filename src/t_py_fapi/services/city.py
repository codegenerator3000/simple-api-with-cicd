from sqlalchemy.ext.asyncio import AsyncSession

from t_py_fapi.models import CityDTO
from t_py_fapi.repositories import CityRepository

from .base import BaseService


class CityService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        self.cities = CityRepository(session)

    async def get_cities(self) -> list[CityDTO]:
        cities = await self.cities.get_all()
        return [CityDTO.model_validate(city) for city in cities]
