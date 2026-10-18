from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from t_py_fapi.models import MarketCreate, MarketDTO
from t_py_fapi.params import GetMarketParams
from t_py_fapi.services import StreetNotFoundError

from .deps import MarketServiceDep

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=list[MarketDTO])
async def get_markets(
    params: Annotated[GetMarketParams, Depends()],
    service: MarketServiceDep,
) -> list[MarketDTO]:
    return await service.get_markets(params)


@router.post("", response_model=MarketDTO, status_code=201)
async def create_market(payload: MarketCreate, service: MarketServiceDep) -> MarketDTO:
    try:
        return await service.create_market(payload=payload)
    except StreetNotFoundError as exc:
        raise HTTPException(status_code=404, detail="street not found") from exc
