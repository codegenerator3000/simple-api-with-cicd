from sqlalchemy import select

from t_py_fapi.database import City

from .base import BaseRepository


class CityRepository(BaseRepository):
    async def get_all(self) -> list[City]:
        return await self._all(select(City).order_by(City.id))
