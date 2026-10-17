from sqlalchemy import select
from sqlalchemy.orm import selectinload

from t_py_fapi.database import Market, Street
from t_py_fapi.params import GetMarketParams

from .base import BaseRepository


class MarketRepository(BaseRepository):
    async def create(self, market_data: Market) -> Market:
        # The caller resolves the street (with its city loaded — see
        # StreetRepository.get_by_id) so it can map the result to a DTO without
        # a lazy load on an async session.
        self.session.add(market_data)
        await self.session.commit()
        return market_data

    async def get_all(self, params: GetMarketParams | None = None) -> list[Market]:
        # street/city chain eager-loaded: callers map markets to DTOs and a lazy
        # load on an async session would raise MissingGreenlet.
        stmt = (
            select(Market)
            .options(selectinload(Market.street).selectinload(Street.city))
            .order_by(Market.id)
        )
        if params is not None:
            for relationship in params.joins():
                stmt = stmt.join(relationship)
            stmt = stmt.where(*params.conditions())
        return await self._all(stmt)
