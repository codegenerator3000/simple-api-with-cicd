from unittest.mock import AsyncMock

from t_py_fapi.models import CityDTO
from t_py_fapi.services import CityService


async def test_get_cities_maps_entities_to_dtos(make_city):
    cities = [make_city(1), make_city(2)]
    service = CityService(AsyncMock())
    service.cities = AsyncMock()
    service.cities.get_all.return_value = cities

    result = await service.get_cities()

    service.cities.get_all.assert_awaited_once()
    assert all(isinstance(city, CityDTO) for city in result)
    assert [city.id for city in result] == [1, 2]
    assert [city.name for city in result] == [city.name for city in cities]


async def test_get_cities_returns_empty_list_when_repository_is_empty():
    service = CityService(AsyncMock())
    service.cities = AsyncMock()
    service.cities.get_all.return_value = []

    assert await service.get_cities() == []
