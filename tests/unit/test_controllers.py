from collections.abc import Callable, Iterator
from datetime import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from t_py_fapi.controllers.deps import (
    get_city_service,
    get_market_service,
    get_street_service,
)
from t_py_fapi.main import app
from t_py_fapi.models import CityDTO, MarketCreate, MarketDTO, StreetDTO
from t_py_fapi.params import GetMarketParams
from t_py_fapi.services import StreetNotFoundError


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Deliberately not used as a context manager: that would run the lifespan
    # and hit the database via the startup seeder. Endpoint tests stub the
    # services instead, so no DB is needed here.
    test_client = TestClient(app)
    yield test_client
    test_client.close()


@pytest.fixture
def override_services() -> Iterator[Callable[..., None]]:
    def apply(
        city_service: object = None,
        street_service: object = None,
        market_service: object = None,
    ) -> None:
        if city_service is not None:
            app.dependency_overrides[get_city_service] = lambda: city_service
        if street_service is not None:
            app.dependency_overrides[get_street_service] = lambda: street_service
        if market_service is not None:
            app.dependency_overrides[get_market_service] = lambda: market_service

    yield apply
    app.dependency_overrides.clear()


def test_get_cities_returns_stubbed_dtos(client, override_services, faker):
    cities = [CityDTO(id=1, name=faker.city()), CityDTO(id=2, name=faker.city())]
    city_service = AsyncMock()
    city_service.get_cities.return_value = cities
    override_services(city_service=city_service)

    response = client.get("/cities")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": cities[0].name},
        {"id": 2, "name": cities[1].name},
    ]
    city_service.get_cities.assert_awaited_once()


def test_get_streets_returns_nested_city(client, override_services, faker):
    street = StreetDTO(
        id=1, name=faker.street_name(), city=CityDTO(id=1, name=faker.city())
    )
    street_service = AsyncMock()
    street_service.get_streets.return_value = [street]
    override_services(street_service=street_service)

    response = client.get("/streets")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": street.name, "city": {"id": 1, "name": street.city.name}}
    ]
    street_service.get_streets.assert_awaited_once()


def test_get_city_streets_passes_city_id_from_path(client, override_services, faker):
    street = StreetDTO(
        id=5,
        name=faker.street_name(),
        city=CityDTO(id=42, name=faker.city()),
    )
    street_service = AsyncMock()
    street_service.get_streets_by_city.return_value = [street]
    override_services(street_service=street_service)

    response = client.get("/cities/42/streets")

    assert response.status_code == 200
    street_service.get_streets_by_city.assert_awaited_once_with(42)
    assert response.json() == [
        {"id": 5, "name": street.name, "city": {"id": 42, "name": street.city.name}}
    ]


def test_get_city_streets_returns_empty_list_for_unknown_city(
    client, override_services
):
    street_service = AsyncMock()
    street_service.get_streets_by_city.return_value = []
    override_services(street_service=street_service)

    response = client.get("/cities/999999/streets")

    assert response.status_code == 200
    assert response.json() == []
    street_service.get_streets_by_city.assert_awaited_once_with(999999)


def market_dto(market_id: int, faker) -> MarketDTO:
    return MarketDTO(
        id=market_id,
        name=faker.company(),
        street=StreetDTO(
            id=1, name=faker.street_name(), city=CityDTO(id=1, name=faker.city())
        ),
        house_number=faker.building_number(),
        opening_time=time(8, 0),
        closing_time=time(18, 0),
    )


def test_get_markets_returns_nested_street_and_city(client, override_services, faker):
    market = market_dto(1, faker)
    market_service = AsyncMock()
    market_service.get_markets.return_value = [market]
    override_services(market_service=market_service)

    response = client.get("/markets")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": market.name,
            "street": {
                "id": 1,
                "name": market.street.name,
                "city": {"id": 1, "name": market.street.city.name},
            },
            "house_number": market.house_number,
            "opening_time": "08:00:00",
            "closing_time": "18:00:00",
        }
    ]


def test_get_markets_passes_every_query_filter_to_the_service(
    client, override_services
):
    market_service = AsyncMock()
    market_service.get_markets.return_value = []
    override_services(market_service=market_service)

    response = client.get(
        "/markets", params={"street_id": 3, "city_id": 7, "is_open": "true"}
    )

    assert response.status_code == 200
    market_service.get_markets.assert_awaited_once()
    passed = market_service.get_markets.await_args.args[0]
    assert isinstance(passed, GetMarketParams)
    assert (passed.street_id, passed.city_id, passed.is_open) == (3, 7, True)


def test_get_markets_drops_the_removed_current_time_query_param(
    client, override_services
):
    """Catches current_time sneaking back into the API as an accepted parameter.

    GetMarketParams declares no such field, so FastAPI cannot parse it and the
    service receives default params only.
    """
    market_service = AsyncMock()
    market_service.get_markets.return_value = []
    override_services(market_service=market_service)

    response = client.get("/markets", params={"current_time": "14:30"})

    assert response.status_code == 200
    market_service.get_markets.assert_awaited_once()
    passed = market_service.get_markets.await_args.args[0]
    assert isinstance(passed, GetMarketParams)
    assert (passed.street_id, passed.city_id, passed.is_open) == (None, None, None)


def test_get_markets_strips_fields_the_response_model_does_not_declare(
    client, override_services, faker
):
    """Catches a dropped response_model, which would leak ORM internals to clients."""
    market = market_dto(1, faker)
    leaky = SimpleNamespace(
        **market.model_dump(), street_id=1, internal_notes="do not ship"
    )
    market_service = AsyncMock()
    market_service.get_markets.return_value = [leaky]
    override_services(market_service=market_service)

    response = client.get("/markets")

    assert response.status_code == 200
    assert "internal_notes" not in response.json()[0]
    assert "street_id" not in response.json()[0]


def test_create_market_returns_201_with_the_created_market(
    client, override_services, faker
):
    market = market_dto(9, faker)
    market_service = AsyncMock()
    market_service.create_market.return_value = market
    override_services(market_service=market_service)

    response = client.post(
        "/markets",
        json={
            "name": market.name,
            "street_id": 1,
            "house_number": market.house_number,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 9
    assert response.json()["street"]["city"]["name"] == market.street.city.name
    market_service.create_market.assert_awaited_once_with(
        payload=MarketCreate(
            name=market.name,
            street_id=1,
            house_number=market.house_number,
            opening_time=time(8, 0),
            closing_time=time(18, 0),
        )
    )


def test_create_market_rejects_a_body_missing_house_number(client, override_services):
    market_service = AsyncMock()
    override_services(market_service=market_service)

    response = client.post(
        "/markets",
        json={
            "name": "Nowy",
            "street_id": 1,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 422
    market_service.create_market.assert_not_awaited()


def test_create_market_returns_404_when_the_street_does_not_exist(
    client, override_services
):
    """Catches an unhandled StreetNotFoundError surfacing as a 500 instead of a 404."""
    market_service = AsyncMock()
    market_service.create_market.side_effect = StreetNotFoundError(999999)
    override_services(market_service=market_service)

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
