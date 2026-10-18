# uv Docker guide: https://docs.astral.sh/uv/guides/integration/docker/
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# The image ships Python 3.14, so disable uv's Python downloads;
# compile bytecode for faster startup and copy (not hardlink) into the venv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies first — better layer caching
COPY pyproject.toml uv.lock .python-version README.md ./
RUN uv sync --locked --no-install-project

# Copy the project source and install the project itself
COPY migrations ./migrations
COPY alembic.ini .
COPY src ./src
RUN uv sync --locked

# Put the venv executables first on PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# fastapi run: production mode, binds 0.0.0.0:8000, auto-detects `app`
CMD ["fastapi", "run", "src/t_py_fapi/main.py"]
