import json
import logging
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from t_py_fapi.database import City, Street
from t_py_fapi.database.session import SessionLocal

from .schemas import CitySeed, SeedData, StreetSeed

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent / "data" / "seed.json"


async def seed_cities_and_streets() -> None:
    """Insert cities and streets from seeders/data/seed.json not yet in the DB.

    Best-effort: logs a warning instead of crashing the app when the schema
    does not exist yet (run `uv run alembic upgrade head`) or the DB is
    unreachable.
    """
    seed_data = _load_seed_data()
    if seed_data is None:
        return

    try:
        async with SessionLocal() as session:
            city_ids, added_cities = await _seed_cities(session, seed_data.cities)
            added_streets = await _seed_streets(
                session, seed_data.streets, city_ids
            )
            await session.commit()
            logger.info(
                "Seed check done: %d cities, %d streets newly inserted",
                added_cities,
                added_streets,
            )
    except SQLAlchemyError as exc:
        logger.warning(
            "Seeding skipped (%s). Is the schema created? "
            "Run: uv run alembic upgrade head",
            exc,
        )


def _load_seed_data() -> SeedData | None:
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return SeedData.model_validate(raw)
    except OSError as exc:
        logger.warning("Could not read seed data from %s: %s", DATA_FILE, exc)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in %s: %s", DATA_FILE, exc)
    except ValidationError as exc:
        logger.warning("Invalid seed data in %s: %s", DATA_FILE, exc)
    return None


async def _seed_cities(
    session: AsyncSession, cities: list[CitySeed]
) -> tuple[dict[str, int], int]:
    """Insert missing cities; return name -> id map and inserted count."""
    city_ids = {
        city.name: city.id for city in (await session.scalars(select(City))).all()
    }
    added = 0
    for item in cities:
        if item.name not in city_ids:
            city = City(name=item.name)
            session.add(city)
            await session.flush()
            city_ids[item.name] = city.id
            added += 1
    return city_ids, added


async def _seed_streets(
    session: AsyncSession, streets: list[StreetSeed], city_ids: dict[str, int]
) -> int:
    """Insert missing streets (city resolved by name); return inserted count."""
    existing = {
        (street.city_id, street.name)
        for street in (await session.scalars(select(Street))).all()
    }
    added = 0
    for item in streets:
        city_id = city_ids.get(item.city)
        if city_id is None:
            logger.warning(
                "Skipping street %r: unknown city %r", item.name, item.city
            )
            continue
        if (city_id, item.name) not in existing:
            session.add(Street(name=item.name, city_id=city_id))
            added += 1
    return added
