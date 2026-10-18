# AGENTS.md

## What this repo is

Small FastAPI + async SQLAlchemy app on MySQL (`asyncmy`), managed with **uv**.
Python **3.14** is pinned in `.python-version` and `mise.toml` — don't change it
casually. `README.md` is the requirements source (entities City → Street →
Market, use-cases); treat it as the spec and expect the code to lag it.

The app is early: `t_py_fapi.main:app` exposes `/health` plus the resource
routes under `controllers/` (`GET /cities`, `GET /cities/{id}/streets`,
`GET /streets`, `GET /markets`, `POST /markets`) and seeds cities/streets on
startup.

## Layout trap: two "models" trees

The names are inverted from the usual convention — don't mix them up:

- `src/t_py_fapi/database/` = **SQLAlchemy ORM** models (`City`, `Street`,
  `Market`; re-exported with `Base`/`intpk` from `database/__init__.py`).
- `src/t_py_fapi/models/` = **Pydantic DTOs** (`CityDTO`, `StreetDTO`,
  `MarketDTO`, and the request model `MarketCreate`).
- `config/database.py` builds `database_url` from `DatabaseSettings` (env
  prefix `DB_`, reads `.env`).

## Commands

- `uv sync` — install/refresh dependencies.
- `uv run fastapi dev src/t_py_fapi/main.py` — dev server with reload.
  Production/Docker uses `fastapi run src/t_py_fapi/main.py`.
- `uv run pytest` — runs the suite: fast unit tests plus integration tests
  against a MySQL testcontainer (needs Docker; `-m "not integration"` skips it).
  See "Quality tooling".
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
- **There is no console script.** The old `fapi` entry point pointed at the
  ASGI `app` instance and raised `TypeError` on every run; it has been removed.
  Use `fastapi dev`/`fastapi run` (see "Commands").

## Seeding

On startup the lifespan calls `seed_cities_and_streets()` (in
`seeders/json_seeder.py`), reading `seeders/data/seed.json`. It is best-effort:
when the schema is missing or the DB is unreachable it logs a warning instead of
crashing. Only cities and streets are seeded (no markets); it is idempotent by
name.

## Market open status

Open status is derived from `opening_time`/`closing_time`, not stored. A window
that wraps midnight (`closing_time <= opening_time`, e.g. 22:00-02:00) is open on
both sides of it. Boundaries are inclusive. The clock lives on the query model:
`GetMarketParams` (`params/market_params.py`) carries a private `selected_time`
stamped from the wall clock at construction, and its `conditions()` feeds
`MarketRepository.get_all(params)`. No time parameter crosses a public
signature, and the API cannot set it.

## Quality tooling

- Tests live under `tests/` in three tiers:
  - `tests/unit/` — no DB; service/controller logic against mocked
    repositories, with `faker`-built ORM entities.
  - `tests/*.py` at the `tests/` root — fast tier on **in-memory SQLite**
    (`create_all`, no Docker): repository queries and the market service.
    Not proof for MySQL-specific behavior.
  - `tests/integration/` — repositories/services/controllers against a
    **MySQL testcontainer** migrated with Alembic; this tier owns
    dialect-specific behavior (e.g. the open-status time comparison).
  `pytest` is configured with `asyncio_mode = "auto"`; integration tests carry
  the `integration` marker (`uv run pytest -m "not integration"` skips Docker).
- Ruff: `uv run ruff check .` (lint) and `uv run ruff format .` / `--check`
  (format). Config lives in `pyproject.toml`; `migrations/versions` is excluded
  (generated files). The ORM models use `from __future__ import annotations`
  with `TYPE_CHECKING` imports.
- CI: `.gitlab-ci.yml` (local GitLab at http://gitlab.local:8929/) runs ruff
  lint/format-check and the full pytest suite on branch pushes and MRs; the
  integration tests use Docker-in-Docker, so the runner must be registered with
  `privileged = true`. The `build` job (default branch/tags only) pushes the
  image to the project's GitLab Container Registry. CI has no `.env`, so the
  pipeline sets placeholder `DB_*` vars (the app requires them at import time).
