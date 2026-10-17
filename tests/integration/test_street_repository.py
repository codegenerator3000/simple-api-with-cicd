import pytest

from t_py_fapi.repositories import StreetRepository

pytestmark = pytest.mark.integration


async def test_get_all_returns_empty_list_when_no_streets(session):
    streets = await StreetRepository(session).get_all()

    assert streets == []


async def test_get_all_returns_all_streets_with_city_loaded(session, street_factory):
    expected = await street_factory(
        [
            ("Berlin", "Unter den Linden"),
            ("Berlin", "Karl-Marx-Allee"),
            ("Paris", "Rue"),
        ]
    )

    streets = await StreetRepository(session).get_all()

    assert [(s.id, s.name) for s in streets] == [(s.id, s.name) for s in expected]
    # city is eager-loaded, so it is usable without a lazy load.
    assert [s.city.name for s in streets] == ["Berlin", "Berlin", "Paris"]


async def test_get_all_by_city_returns_only_that_city(session, street_factory):
    expected = await street_factory([("Berlin", "Unter den Linden"), ("Paris", "Rue")])
    berlin = next(s for s in expected if s.city.name == "Berlin")

    streets = await StreetRepository(session).get_all_by_city(berlin.city_id)

    assert [(s.id, s.name) for s in streets] == [(berlin.id, berlin.name)]
    assert streets[0].city.name == "Berlin"


async def test_get_all_by_city_returns_empty_list_for_unknown_city(
    session, street_factory
):
    await street_factory([("Berlin", "Unter den Linden")])

    streets = await StreetRepository(session).get_all_by_city(999_999)

    assert streets == []


async def test_get_by_id_returns_the_street_with_city_loaded(
    session, session_factory, street_factory
):
    (berlin,) = await street_factory([("Berlin", "Unter den Linden")])

    async with session_factory() as other_session:
        street = await StreetRepository(other_session).get_by_id(berlin.id)

        # city is eager-loaded, so a fresh session can use it without a lazy load.
        assert street is not None
        assert street.name == "Unter den Linden"
        assert street.city.name == "Berlin"


async def test_get_by_id_returns_none_for_unknown_id(session, street_factory):
    await street_factory([("Berlin", "Unter den Linden")])

    assert await StreetRepository(session).get_by_id(999_999) is None
