from sqlalchemy.ext.asyncio import AsyncSession

from t_py_fapi.database import Market
from t_py_fapi.models import MarketCreate, MarketDTO
from t_py_fapi.params import GetMarketParams
from t_py_fapi.repositories import MarketRepository, StreetRepository

from .base import BaseService
from .errors import StreetNotFoundError


class MarketService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        self.markets = MarketRepository(session)
        self.streets = StreetRepository(session)

    async def create_market(self, *, payload: MarketCreate) -> MarketDTO:
        street = await self.streets.get_by_id(payload.street_id)
        if street is None:
            raise StreetNotFoundError(payload.street_id)

        new_market = Market(
            name=payload.name,
            street=street,
            house_number=payload.house_number,
            opening_time=payload.opening_time,
            closing_time=payload.closing_time,
        )
        market = await self.markets.create(new_market)

        return MarketDTO.model_validate(market)

    async def get_markets(self, params: GetMarketParams) -> list[MarketDTO]:
        markets = await self.markets.get_all(params)
        return [MarketDTO.model_validate(market) for market in markets]
