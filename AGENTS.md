# AGENTS.md

## What this repo is

Small FastAPI + async SQLAlchemy app on MySQL (`asyncmy`), managed with **uv**.
Python **3.14** is pinned in `.python-version` and `mise.toml` — don't change it
casually. `README.md` is the requirements source (entities City → Street →
Market, use-cases); treat it as the spec and expect the code to lag it.

The app is early: `t_py_fapi.main:app` exposes only `/health` today and seeds
cities/streets on startup.

## Layout trap: two "models" trees

The names are inverted from the usual convention — don't mix them up:

- `src/t_py_fapi/database/` = **SQLAlchemy ORM** models (`City`, `Street`,
  `Market`; re-exported with `Base`/`intpk` from `database/__init__.py`).
- `src/t_py_fapi/models/` = **Pydantic DTOs** (`CityDTO`, `StreetDTO`,
  `MarketDTO`).
- `config/database.py` builds `database_url` from `DatabaseSettings` (env
  prefix `DB_`, reads `.env`).

## Commands

- `uv sync` — install/refresh dependencies.
- `uv run fastapi dev src/t_py_fapi/main.py` — dev server with reload.
  Production/Docker uses `fastapi run src/t_py_fapi/main.py`.
- `uv run pytest` — there are **no tests**; collecting nothing is expected.
- `uv run alembic upgrade head` / `uv run alembic revision --autogenerate -m "..."`.
- `docker compose up --build` — MySQL 8.4 + API (`:8000`, DB `:3306`).

## Setup and gotchas

- **`.env` is gitignored and not committed.** A fresh clone has none, and every
  command that imports the app fails without it (`DatabaseSettings` requires
  all fields). Provide `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
  `DB_PASSWORD`, and (for compose) `MYSQL_ROOT_PASSWORD`. The same `.env` is
  read by the app and by `docker-compose.yaml`.
- **Nothing starts the database for you.** Local MySQL isn't running by default;
  run `docker compose up -d db` before migrations or `fastapi dev`.
  `DB_HOST=localhost` only works when the DB is reachable from the host.
- **Never create tables outside Alembic.** `migrations/versions/4f976b244281_...`
  now carries the initial `cities`/`streets`/`markets` schema, so
  `uv run alembic upgrade head` builds it on an empty DB. Autogenerate diffs the
  live DB against the ORM; if tables were created by hand (or by `create_all`)
  the diff is empty and you get a no-op migration — that is exactly what once
  left the initial migration empty. Use `uv run alembic check` to detect drift.
  `migrations/env.py` imports `t_py_fapi.database`, so `Base.metadata` is
  populated for autogenerate.
- **The `fapi` console script is broken.** `[project.scripts] fapi =
  "t_py_fapi.main:app"` points at the ASGI `app` instance, so `uv run fapi`
  raises `TypeError: FastAPI.__call__() missing ...`. Use `fastapi dev`/`run`
  instead. (`main.py`'s `main()` helper is not wired to any script.)
## Seeding

On startup the lifespan calls `seed_cities_and_streets()` (in
`seeders/json_seeder.py`), reading `seeders/data/seed.json`. It is best-effort:
when the schema is missing or the DB is unreachable it logs a warning instead of
crashing. Only cities and streets are seeded (no markets); it is idempotent by
name.

## Known spec/code mismatch

README and `MarketDTO` use `home_address`, but ORM `Market` uses `house_number`.
Reconcile this before wiring market endpoints. Market open status is derived from
`opening_time`/`closing_time` and is not stored.

## Quality tooling

No test directory, pytest/lint/format/typecheck config, or CI exists. Add tests
under `tests/` following the default layout.
