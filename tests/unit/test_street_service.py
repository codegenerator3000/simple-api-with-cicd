from unittest.mock import AsyncMock

from t_py_fapi.models import CityDTO, StreetDTO
from t_py_fapi.services import StreetService


async def test_get_streets_maps_entities_with_nested_city(make_city, make_street):
    city = make_city(7)
    streets = [make_street(1, city), make_street(2, city)]
    service = StreetService(AsyncMock())
    service.streets = AsyncMock()
    service.streets.get_all.return_value = streets

    result = await service.get_streets()

    service.streets.get_all.assert_awaited_once()
    assert all(isinstance(street, StreetDTO) for street in result)
    assert [street.id for street in result] == [1, 2]
    assert [street.name for street in result] == [street.name for street in streets]
    assert result[0].city == CityDTO(id=city.id, name=city.name)


async def test_get_streets_by_city_maps_only_requested_city(make_city, make_street):
    berlin, paris = make_city(1), make_city(2)
    streets = [make_street(10, berlin), make_street(11, berlin)]
    service = StreetService(AsyncMock())
    service.streets = AsyncMock()
    service.streets.get_all_by_city.return_value = streets

    result = await service.get_streets_by_city(berlin.id)

    service.streets.get_all_by_city.assert_awaited_once_with(berlin.id)
    assert [street.id for street in result] == [10, 11]
    assert all(street.city.id == berlin.id for street in result)
    assert all(street.city.id != paris.id for street in result)


async def test_get_streets_by_city_returns_empty_list_when_repository_is_empty():
    service = StreetService(AsyncMock())
    service.streets = AsyncMock()
    service.streets.get_all_by_city.return_value = []

    assert await service.get_streets_by_city(999) == []
