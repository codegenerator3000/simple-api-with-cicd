import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from t_py_fapi.controllers import router as api_router
from t_py_fapi.seeders.json_seeder import seed_cities_and_streets


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO)
    await seed_cities_and_streets()
    yield


app = FastAPI(title="t-py-fapi", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
