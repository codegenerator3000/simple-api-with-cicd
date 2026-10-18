from datetime import time

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from t_py_fapi.database import City, Market, Street
from t_py_fapi.params import GetMarketParams
from t_py_fapi.repositories import MarketRepository


async def add_market(repo: MarketRepository, street: Street, **overrides) -> Market:
    fields = {
        "name": "Market",
        "street": street,
        "house_number": "1",
        "opening_time": time(8, 0),
        "closing_time": time(18, 0),
    }
    return await repo.create(Market(**{**fields, **overrides}))


def timed_params(*, is_open: bool, selected: time) -> GetMarketParams:
    """Params with a pinned clock: GetMarketParams otherwise stamps
    selected_time from the wall clock at construction."""
    params = GetMarketParams(is_open=is_open)
    params._selected_time = selected
    return params


async def test_create_commits_the_market(
    session: AsyncSession,
    session_factory: async_sessionmaker[AsyncSession],
    street: Street,
) -> None:
    """Catches a create() that flushes but never commits: the row is gone on reconnect."""
    repo = MarketRepository(session)
    created = await repo.create(
        Market(
            name="Hala Targowa",
            street=street,
            house_number="1",
            opening_time=time(8, 0),
            closing_time=time(18, 0),
        )
    )

    async with session_factory() as other_session:
        rows = (await other_session.scalars(select(Market))).all()

    assert [row.id for row in rows] == [created.id]
    assert rows[0].name == "Hala Targowa"
    assert rows[0].house_number == "1"


async def test_get_all_returns_markets_in_insertion_order(
    session: AsyncSession, street: Street
) -> None:
    """Catches a dropped order_by: results would come back in arbitrary order."""
    repo = MarketRepository(session)
    for name in ("Zebra", "Alpha", "Mid"):
        await add_market(repo, street, name=name)

    markets = await repo.get_all()

    assert [market.name for market in markets] == ["Zebra", "Alpha", "Mid"]


async def test_get_all_filters_by_street(session: AsyncSession, street: Street) -> None:
    """Catches a street_id filter that is ignored or applied as an OR."""
    repo = MarketRepository(session)
    other_street = Street(name="Dluga", city_id=street.city_id)
    session.add(other_street)
    await session.commit()
    await add_market(repo, street, name="On Dluga")
    await add_market(repo, other_street, name="On Ogarna")

    markets = await repo.get_all(GetMarketParams(street_id=street.id))

    assert [market.name for market in markets] == ["On Dluga"]


async def test_get_all_filters_by_city(session: AsyncSession, street: Street) -> None:
    """Catches a city_id filter that is missing or matches only the first street."""
    repo = MarketRepository(session)
    other_city = City(name="Gdynia")
    session.add(other_city)
    await session.commit()
    other_street = Street(name="Swietego Ducha", city_id=other_city.id)
    session.add(other_street)
    await session.commit()
    await add_market(repo, street, name="Gdansk market")
    await add_market(repo, other_street, name="Gdynia market")

    markets = await repo.get_all(GetMarketParams(city_id=street.city_id))

    assert [market.name for market in markets] == ["Gdansk market"]


# (opening, closing, now, expected_open) -- hand-checked, not computed.
SAME_DAY_CASES = [
    (time(8, 0), time(18, 0), time(12, 0), True),
    (time(8, 0), time(18, 0), time(7, 59), False),
    (time(8, 0), time(18, 0), time(18, 1), False),
    (time(8, 0), time(18, 0), time(8, 0), True),
    (time(8, 0), time(18, 0), time(18, 0), True),
]

# A market open 22:00-02:00 wraps midnight; the plain window test cannot express it.
OVERNIGHT_CASES = [
    (time(22, 0), time(2, 0), time(23, 30), True),
    (time(22, 0), time(2, 0), time(1, 30), True),
    (time(22, 0), time(2, 0), time(2, 0), True),
    (time(22, 0), time(2, 0), time(22, 0), True),
    (time(22, 0), time(2, 0), time(2, 1), False),
    (time(22, 0), time(2, 0), time(21, 59), False),
    (time(22, 0), time(2, 0), time(12, 0), False),
]


@pytest.mark.parametrize(("opening", "closing", "now", "expected_open"), SAME_DAY_CASES)
async def test_get_all_is_open_covers_the_whole_day_window(
    session: AsyncSession,
    street: Street,
    opening: time,
    closing: time,
    now: time,
    expected_open: bool,
) -> None:
    """Catches wrong comparison operators and off-by-one boundary handling."""
    repo = MarketRepository(session)
    await add_market(repo, street, opening_time=opening, closing_time=closing)

    open_markets = await repo.get_all(timed_params(is_open=True, selected=now))
    closed_markets = await repo.get_all(timed_params(is_open=False, selected=now))

    assert bool(open_markets) is expected_open
    assert bool(closed_markets) is not expected_open


@pytest.mark.parametrize(
    ("opening", "closing", "now", "expected_open"), OVERNIGHT_CASES
)
async def test_get_all_is_open_handles_windows_that_wrap_midnight(
    session: AsyncSession,
    street: Street,
    opening: time,
    closing: time,
    now: time,
    expected_open: bool,
) -> None:
    """Catches a window test that only handles markets opening before they close."""
    repo = MarketRepository(session)
    await add_market(repo, street, opening_time=opening, closing_time=closing)

    open_markets = await repo.get_all(timed_params(is_open=True, selected=now))
    closed_markets = await repo.get_all(timed_params(is_open=False, selected=now))

    assert bool(open_markets) is expected_open
    assert bool(closed_markets) is not expected_open


async def test_get_all_is_open_ignores_selected_time_when_not_filtering_by_open(
    session: AsyncSession, street: Street
) -> None:
    """Catches is_open's absence letting the selected time leak in as a filter."""
    repo = MarketRepository(session)
    await add_market(repo, street, opening_time=time(8, 0), closing_time=time(18, 0))

    params = GetMarketParams()
    params._selected_time = time(3, 0)
    markets = await repo.get_all(params)

    assert [market.name for market in markets] == ["Market"]


async def test_get_all_combines_street_city_and_open_filters(
    session: AsyncSession, street: Street
) -> None:
    """Catches filters overwriting each other instead of narrowing the same query."""
    repo = MarketRepository(session)
    other_city = City(name="Gdynia")
    session.add(other_city)
    await session.commit()
    other_street = Street(name="Swietego Ducha", city_id=other_city.id)
    same_city_street = Street(name="Dluga", city_id=street.city_id)
    session.add_all([other_street, same_city_street])
    await session.commit()

    await add_market(
        repo,
        street,
        name="wanted",
        opening_time=time(8, 0),
        closing_time=time(18, 0),
    )
    await add_market(
        repo,
        same_city_street,
        name="wrong street",
        opening_time=time(8, 0),
        closing_time=time(18, 0),
    )
    await add_market(
        repo,
        street,
        name="closed",
        opening_time=time(19, 0),
        closing_time=time(20, 0),
    )
    await add_market(
        repo,
        other_street,
        name="wrong city",
        opening_time=time(8, 0),
        closing_time=time(18, 0),
    )

    params = GetMarketParams(street_id=street.id, city_id=street.city_id, is_open=True)
    params._selected_time = time(12, 0)
    markets = await repo.get_all(params)

    assert [market.name for market in markets] == ["wanted"]
