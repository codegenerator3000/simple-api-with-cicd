from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from t_py_fapi.config.database import database_url

engine = create_async_engine(database_url)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with SessionLocal() as session:
        yield session
