from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from t_py_fapi.database import Base, City, Street

# Fast test tier: in-memory SQLite, schema via create_all (not Alembic — the
# schema only needs to outlive one test). Good for query shape, ordering and
# service wiring, but NOT proof for dialect-specific behavior such as MySQL
# time comparison: tests/integration/ owns that, against a real MySQL container.


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """A throwaway in-memory SQLite engine with the schema created."""
    db_engine = create_async_engine("sqlite+aiosqlite://")
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield db_engine
    await db_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as db_session:
        yield db_session


@pytest_asyncio.fixture
async def city(session: AsyncSession) -> City:
    db_city = City(name="Gdansk")
    session.add(db_city)
    await session.commit()
    return db_city


@pytest_asyncio.fixture
async def street(session: AsyncSession, city: City) -> Street:
    db_street = Street(name="Dluga", city_id=city.id)
    session.add(db_street)
    await session.commit()
    return db_street
