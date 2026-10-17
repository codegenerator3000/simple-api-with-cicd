from fastapi import APIRouter

from t_py_fapi.models import StreetDTO

from .deps import StreetServiceDep

router = APIRouter(prefix="/streets", tags=["streets"])


@router.get("", response_model=list[StreetDTO])
async def get_streets(service: StreetServiceDep) -> list[StreetDTO]:
    return await service.get_streets()
