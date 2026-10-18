from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from t_py_fapi.config.database import database_url

# The engine is built at import time from DB_* (config.database reads .env), so
# importing anything that pulls in the app requires a .env with DB_* set.
engine = create_async_engine(database_url)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
