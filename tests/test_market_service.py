from datetime import datetime, time, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from t_py_fapi.database import Street
from t_py_fapi.models import MarketCreate
from t_py_fapi.params import GetMarketParams
from t_py_fapi.services import MarketService, StreetNotFoundError


def market_payload(street_id: int, **overrides) -> MarketCreate:
    fields = {
        "name": "Hala Targowa",
        "street_id": street_id,
        "house_number": "12",
        "opening_time": time(8, 0),
        "closing_time": time(18, 0),
    }
    return MarketCreate(**{**fields, **overrides})


async def test_create_market_returns_the_new_market_as_a_dto(
    session: AsyncSession, street: Street
) -> None:
    """Catches a DTO built without the created market's real id and times."""
    service = MarketService(session)

    dto = await service.create_market(payload=market_payload(street.id))

    assert dto.id > 0
    assert dto.name == "Hala Targowa"
    assert dto.house_number == "12"
    assert dto.opening_time == time(8, 0)
    assert dto.closing_time == time(18, 0)


async def test_create_market_response_carries_the_street_and_its_city(
    session: AsyncSession, street: Street
) -> None:
    """Catches unloaded relationships: without them this raises MissingGreenlet."""
    service = MarketService(session)

    dto = await service.create_market(payload=market_payload(street.id))

    assert dto.street.id == street.id
    assert dto.street.name == "Dluga"
    assert dto.street.city.id == street.city_id
    assert dto.street.city.name == "Gdansk"


async def test_get_markets_returns_markets_as_dtos(
    session: AsyncSession,
    session_factory: async_sessionmaker[AsyncSession],
    street: Street,
) -> None:
    """Catches a service returning ORM objects, or relying on a warm identity map.

    Reads through a fresh session, as a real request would: a market fetched there
    has no relationship loaded unless the query eager-loads it.
    """
    await MarketService(session).create_market(payload=market_payload(street.id))

    async with session_factory() as other_session:
        markets = await MarketService(other_session).get_markets(GetMarketParams())

    assert [market.name for market in markets] == ["Hala Targowa"]
    assert markets[0].house_number == "12"
    assert markets[0].street.name == "Dluga"
    assert markets[0].street.city.name == "Gdansk"


async def test_get_markets_filters_by_open_status(
    session: AsyncSession, street: Street
) -> None:
    """Catches the service dropping or mis-ordering filters passed to the repository.

    GetMarketParams stamps selected_time from the wall clock at construction,
    so both windows are built around now to stay deterministic at any hour.
    """
    service = MarketService(session)
    now = datetime.now()
    windows = {
        "open now": (
            (now - timedelta(hours=1)).time(),
            (now + timedelta(hours=1)).time(),
        ),
        "shut": (
            (now + timedelta(hours=2)).time(),
            (now + timedelta(hours=3)).time(),
        ),
    }
    for name, (opening, closing) in windows.items():
        await service.create_market(
            payload=market_payload(
                street.id,
                name=name,
                house_number="1",
                opening_time=opening,
                closing_time=closing,
            )
        )

    open_markets = await service.get_markets(GetMarketParams(is_open=True))
    closed_markets = await service.get_markets(GetMarketParams(is_open=False))

    assert [market.name for market in open_markets] == ["open now"]
    assert [market.name for market in closed_markets] == ["shut"]


async def test_create_market_raises_when_the_street_does_not_exist(
    session: AsyncSession,
) -> None:
    """Catches a missing street surfacing as a DB error instead of a domain error."""
    service = MarketService(session)

    with pytest.raises(StreetNotFoundError):
        await service.create_market(
            payload=market_payload(999_999, name="Oszustwo", house_number="1")
        )
