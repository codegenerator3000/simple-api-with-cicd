import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator, Sequence
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.community.mysql import MySqlContainer

from t_py_fapi.database import City, Street

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "alembic.ini"

# Reverse foreign-key order so the deletes are legal.
TABLES = ("markets", "streets", "cities")

CityFactory = Callable[..., Awaitable[list[City]]]
StreetFactory = Callable[[Sequence[tuple[str, str]]], Awaitable[list[Street]]]


def _run_migrations(env: dict[str, str]) -> None:
    """Apply the migrations to the container from a fresh interpreter.

    t_py_fapi.config.database resolves database_url at import time. If anything
    has already imported it in this process (a controller unit test importing
    the app does), the cached .env URL would send the migration to the dev
    database instead. A subprocess guarantees the container env is what gets read.
    """
    script = (
        "from alembic import command\n"
        "from alembic.config import Config\n"
        f"command.upgrade(Config({str(ALEMBIC_INI)!r}), 'head')\n"
    )
    subprocess.run([sys.executable, "-c", script], env=env, check=True, cwd=REPO_ROOT)


@pytest.fixture(scope="session")
def mysql_container() -> Iterator[MySqlContainer]:
    with MySqlContainer("mysql:8.4") as container:
        yield container


@pytest.fixture(scope="session")
def session_factory(mysql_container: MySqlContainer) -> Iterator[async_sessionmaker]:
    """Migrate a throwaway MySQL container and expose a session factory.

    The schema is built by running the real migrations rather than
    create_all, per the project rule that tables are never created outside
    Alembic.
    """
    host = mysql_container.get_container_host_ip()
    port = mysql_container.get_exposed_port(3306)

    _run_migrations(
        {
            **os.environ,
            "DB_HOST": host,
            "DB_PORT": str(port),
            "DB_NAME": mysql_container.dbname,
            "DB_USER": mysql_container.username,
            "DB_PASSWORD": mysql_container.password,
        }
    )

    url = URL.create(
        "mysql+asyncmy",
        username=mysql_container.username,
        password=mysql_container.password,
        host=host,
        port=port,
        database=mysql_container.dbname,
    )
    # NullPool so each session opens its own connection and none is reused
    # across the per-test event loops pytest-asyncio creates.
    engine = create_async_engine(url, poolclass=NullPool)
    try:
        yield async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    finally:
        asyncio.run(engine.dispose())


@pytest.fixture
async def session(session_factory: async_sessionmaker) -> AsyncIterator[AsyncSession]:
    async with session_factory() as db_session:
        yield db_session


@pytest.fixture(autouse=True)
async def clean_tables(session: AsyncSession) -> AsyncIterator[None]:
    """Give every integration test an empty database."""
    async with session.begin():
        for table in TABLES:
            await session.execute(text(f"DELETE FROM {table}"))
    yield


@pytest.fixture
async def city_factory(session: AsyncSession) -> CityFactory:
    """Persist cities by name, in the order given."""

    async def factory(*names: str) -> list[City]:
        cities = [City(name=name) for name in names]
        session.add_all(cities)
        await session.commit()
        return cities

    return factory


@pytest.fixture
async def street_factory(session: AsyncSession) -> StreetFactory:
    """Persist (city_name, street_name) pairs, reusing a city per name.

    Each test starts with an empty database, so caching created cities by
    name within a single test is enough.
    """
    by_name: dict[str, City] = {}

    async def factory(pairs: Sequence[tuple[str, str]]) -> list[Street]:
        new_names = [
            name
            for name in dict.fromkeys(city for city, _ in pairs)
            if name not in by_name
        ]
        new_cities = [City(name=name) for name in new_names]
        session.add_all(new_cities)
        await session.flush()
        by_name.update({city.name: city for city in new_cities})

        streets = [
            Street(name=street_name, city_id=by_name[city_name].id)
            for city_name, street_name in pairs
        ]
        session.add_all(streets)
        await session.commit()
        return streets

    return factory
