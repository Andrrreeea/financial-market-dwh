from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import DataSourceCreate
from app.services.data_source_service import DataSourceService


router = APIRouter(
    prefix="/data-sources",
    tags=["Data Sources"]
)


@router.post("/")
async def create_data_source(data_source: DataSourceCreate):
    return await DataSourceService.create_data_source(
        data_source.model_dump()
    )


@router.get("/")
async def get_data_sources(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    return await DataSourceService.get_all_data_sources(
        offset=offset,
        limit=limit
    )


@router.get("/{data_source_id}")
async def get_data_source_by_id(data_source_id: str):
    data_source = await DataSourceService.get_data_source(data_source_id)

    if data_source is None:
        raise HTTPException(
            status_code=404,
            detail="Data source not found"
        )

    return data_source