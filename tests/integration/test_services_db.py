import pytest

from t_py_fapi.services import CityService, StreetService

pytestmark = pytest.mark.integration


async def test_get_cities_returns_dtos(session, city_factory):
    await city_factory("Berlin")
    await city_factory("Paris")

    cities = await CityService(session).get_cities()

    assert [c.name for c in cities] == ["Berlin", "Paris"]


async def test_get_streets_returns_dtos_with_nested_city(session, street_factory):
    await street_factory([("Berlin", "Unter den Linden"), ("Paris", "Rue")])

    streets = await StreetService(session).get_streets()

    assert [s.name for s in streets] == ["Unter den Linden", "Rue"]
    assert [s.city.name for s in streets] == ["Berlin", "Paris"]


async def test_get_streets_by_city_returns_dtos_for_that_city(session, street_factory):
    created = await street_factory([("Berlin", "Unter den Linden"), ("Paris", "Rue")])
    paris = next(s for s in created if s.city.name == "Paris")

    streets = await StreetService(session).get_streets_by_city(paris.city_id)

    assert [s.name for s in streets] == ["Rue"]
    assert streets[0].city.name == "Paris"
