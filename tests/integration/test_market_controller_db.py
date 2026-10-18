from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from datetime import datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from t_py_fapi.controllers.deps import get_market_service
from t_py_fapi.database import City, Market
from t_py_fapi.main import app
from t_py_fapi.services import MarketService

pytestmark = pytest.mark.integration


@pytest.fixture
def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> Iterator[TestClient]:
    """A TestClient whose requests run against the MySQL container.

    Built without the context manager so the lifespan seeder does not run. Only
    the market service dependency is redirected -- leaving the others pointed at
    the development database.
    """

    async def get_service() -> AsyncIterator[MarketService]:
        async with session_factory() as db_session:
            yield MarketService(db_session)

    test_client = TestClient(app)
    app.dependency_overrides[get_market_service] = get_service
    yield test_client
    app.dependency_overrides.clear()
    test_client.close()


@pytest.fixture
async def market_factory(
    session: AsyncSession, street_factory
) -> AsyncIterator[Callable[..., Awaitable[list[Market]]]]:
    """Persist markets, creating the street (and city) each one sits on.

    Each spec is (name, city, house_number, opening, closing).
    """

    async def factory(
        *specs: tuple[str, str, str, str, str],
    ) -> list[Market]:
        pairs = [(city, f"{name}-street") for name, city, _, _, _ in specs]
        streets = await street_factory(pairs)
        by_city = {street.city.name: street for street in streets}

        markets = [
            Market(
                name=name,
                street_id=by_city[city].id,
                house_number=house_number,
                opening_time=time.fromisoformat(opening),
                closing_time=time.fromisoformat(closing),
            )
            for name, city, house_number, opening, closing in specs
        ]
        session.add_all(markets)
        await session.commit()
        return markets

    return factory


async def test_get_markets_returns_persisted_markets(client, market_factory):
    await market_factory(("Hala Targowa", "Berlin", "12", "08:00", "18:00"))

    response = client.get("/markets")

    assert response.status_code == 200
    body = response.json()
    assert [m["name"] for m in body] == ["Hala Targowa"]
    assert body[0]["house_number"] == "12"
    assert body[0]["street"]["city"]["name"] == "Berlin"


async def test_post_market_persists_and_returns_it_with_nested_relations(
    client, session, street_factory
):
    streets = await street_factory([("Berlin", "Unter den Linden")])

    response = client.post(
        "/markets",
        json={
            "name": "Nowy Targ",
            "street_id": streets[0].id,
            "house_number": "7",
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Nowy Targ"
    assert body["street"]["name"] == "Unter den Linden"
    assert body["street"]["city"]["name"] == "Berlin"

    stored = (await session.scalars(select(Market))).all()
    assert [m.name for m in stored] == ["Nowy Targ"]
    assert stored[0].house_number == "7"


async def test_post_market_with_unknown_street_returns_404(client, street_factory):
    await street_factory([("Berlin", "Unter den Linden")])

    response = client.post(
        "/markets",
        json={
            "name": "Oszustwo",
            "street_id": 999999,
            "house_number": "1",
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "street not found"


async def test_get_markets_filters_by_open_status_against_real_mysql(
    client, market_factory
):
    """Real MySQL, not SQLite: guards the time comparison on the actual dialect.

    The API takes no current_time anymore (GetMarketParams stamps it from the
    wall clock at construction), so both windows are built around now to keep
    the expectation deterministic at any hour.
    """
    now = datetime.now()
    await market_factory(
        (
            "open now",
            "Berlin",
            "1",
            (now - timedelta(hours=1)).time().isoformat(),
            (now + timedelta(hours=1)).time().isoformat(),
        ),
        (
            "shut",
            "Hamburg",
            "2",
            (now + timedelta(hours=2)).time().isoformat(),
            (now + timedelta(hours=3)).time().isoformat(),
        ),
    )

    open_names = [
        market["name"]
        for market in client.get("/markets", params={"is_open": "true"}).json()
    ]
    shut_names = [
        market["name"]
        for market in client.get("/markets", params={"is_open": "false"}).json()
    ]

    assert open_names == ["open now"]
    assert shut_names == ["shut"]


async def test_get_markets_filters_by_city_against_real_mysql(
    client, market_factory, session
):
    await market_factory(
        ("berlin market", "Berlin", "1", "08:00", "18:00"),
        ("hamburg market", "Hamburg", "2", "08:00", "18:00"),
    )
    cities = (await session.scalars(select(City))).all()
    city_id = next(city.id for city in cities if city.name == "Berlin")

    response = client.get("/markets", params={"city_id": city_id})

    assert [m["name"] for m in response.json()] == ["berlin market"]
