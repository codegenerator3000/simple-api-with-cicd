from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from t_py_fapi.database.session import get_session
from t_py_fapi.services import CityService, MarketService, StreetService


def get_city_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CityService:
    return CityService(session)


def get_street_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StreetService:
    return StreetService(session)


def get_market_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MarketService:
    return MarketService(session)


CityServiceDep = Annotated[CityService, Depends(get_city_service)]
StreetServiceDep = Annotated[StreetService, Depends(get_street_service)]
MarketServiceDep = Annotated[MarketService, Depends(get_market_service)]
