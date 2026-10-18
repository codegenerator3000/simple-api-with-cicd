import pytest

from t_py_fapi.repositories import CityRepository

pytestmark = pytest.mark.integration


async def test_get_all_returns_empty_list_when_no_cities(session):
    cities = await CityRepository(session).get_all()

    assert cities == []


async def test_get_all_returns_all_cities_ordered_by_id(session, city_factory):
    expected = await city_factory("Berlin", "Paris")

    cities = await CityRepository(session).get_all()

    assert [(c.id, c.name) for c in cities] == [(c.id, c.name) for c in expected]
