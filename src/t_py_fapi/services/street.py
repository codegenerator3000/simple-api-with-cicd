from sqlalchemy.ext.asyncio import AsyncSession

from t_py_fapi.models import StreetDTO
from t_py_fapi.repositories import StreetRepository

from .base import BaseService


class StreetService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        self.streets = StreetRepository(session)

    async def get_streets(self) -> list[StreetDTO]:
        streets = await self.streets.get_all()
        return [StreetDTO.model_validate(street) for street in streets]

    async def get_streets_by_city(self, city_id: int) -> list[StreetDTO]:
        streets = await self.streets.get_all_by_city(city_id)
        return [StreetDTO.model_validate(street) for street in streets]
