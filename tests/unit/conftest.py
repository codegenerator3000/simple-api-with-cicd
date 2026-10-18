from collections.abc import Callable

import pytest
from faker import Faker

from t_py_fapi.database import City, Street


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def make_city(faker: Faker) -> Callable[[int], City]:
    """Build an unsaved City ORM entity with a fake name."""

    def factory(city_id: int) -> City:
        return City(id=city_id, name=faker.city())

    return factory


@pytest.fixture
def make_street(
    faker: Faker, make_city: Callable[[int], City]
) -> Callable[[int, City], Street]:
    """Build an unsaved Street ORM entity attached to an unsaved City."""

    def factory(street_id: int, city: City) -> Street:
        return Street(id=street_id, name=faker.street_name(), city=city)

    return factory
