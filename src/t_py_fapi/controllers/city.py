from fastapi import APIRouter

from t_py_fapi.models import CityDTO, StreetDTO

from .deps import CityServiceDep, StreetServiceDep

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", response_model=list[CityDTO])
async def get_cities(service: CityServiceDep) -> list[CityDTO]:
    return await service.get_cities()


@router.get("/{city_id}/streets", response_model=list[StreetDTO])
async def get_city_streets(city_id: int, service: StreetServiceDep) -> list[StreetDTO]:
    return await service.get_streets_by_city(city_id)
