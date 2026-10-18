from sqlalchemy import select
from sqlalchemy.orm import selectinload

from t_py_fapi.database import Street

from .base import BaseRepository

# city is eager-loaded on every street query: callers map a street to a DTO (or
# attach it to a market) and a lazy load on an async session would raise
# MissingGreenlet. One definition so no street query can forget it.
_city_loaded = selectinload(Street.city)


class StreetRepository(BaseRepository):
    async def get_all(self) -> list[Street]:
        stmt = select(Street).options(_city_loaded).order_by(Street.id)
        return await self._all(stmt)

    async def get_by_id(self, street_id: int) -> Street | None:
        stmt = select(Street).where(Street.id == street_id).options(_city_loaded)
        return await self.session.scalar(stmt)

    async def get_all_by_city(self, city_id: int) -> list[Street]:
        stmt = (
            select(Street)
            .where(Street.city_id == city_id)
            .options(_city_loaded)
            .order_by(Street.id)
        )
        return await self._all(stmt)
