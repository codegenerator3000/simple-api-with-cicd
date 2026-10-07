# AGENTS.md

## What this repo is

Early-stage FastAPI project ("Simple app as warm-up"). The only code is a stub:
`src/t_py_fapi/__init__.py` (`main()` prints a hello message). The real
specification lives in `README.md` — entities (Market, City, Street) and
use-cases. Treat README.md as the requirements source; it may lag behind or
lead the code.

## Toolchain

- Managed by **uv** (build backend `uv_build`, `src/` layout). Python **3.14**
  is pinned in both `.python-version` and `mise.toml` — do not change the
  Python version casually.
- Always run things through uv so the right interpreter/venv is used:
  - `uv sync` — install/refresh dependencies
  - `uv run t-py-fapi` — run the console script (calls `t_py_fapi:main`)
  - `uv run python ...` / `uv run pytest` — run ad-hoc code or tests

## Testing

- `pytest` is a declared dependency, but there is currently **no test
  directory, no pytest config, and no tests**. `uv run pytest` collects
  nothing — this is expected, not a failure.
- When adding tests, follow the default layout (e.g. `tests/`) unless
  project conventions say otherwise; no lint, format, typecheck, or CI
  configuration exists yet in this repo.

## Planned architecture (not yet implemented)

Dependencies already declared for the target design:

- `fastapi[standard]` — web framework (includes the dev server via
  `fastapi dev`)
- `alembic` — database migrations

Nothing in the code wires these up yet: no app module, no database config, no
migrations. If you add them, README.md's entities and use-cases define the
intended data model (City → Street → Market relationships).
