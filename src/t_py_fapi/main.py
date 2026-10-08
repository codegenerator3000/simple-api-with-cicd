import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from t_py_fapi.seeders.json_seeder import seed_cities_and_streets


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO)
    await seed_cities_and_streets()
    yield


app = FastAPI(title="t-py-fapi", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    uvicorn.run("t_py_fapi.main:app", host="0.0.0.0", port=8000)
