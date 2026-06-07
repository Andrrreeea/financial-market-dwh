from datetime import date
from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import TimeSeriesBatchIngest
from app.services.time_series_service import TimeSeriesService


router = APIRouter(
    tags=["Time Series Data"]
)


@router.post("/data/ingest")
async def ingest_time_series(batch: TimeSeriesBatchIngest):
    return await TimeSeriesService.ingest_records(
        [record.model_dump() for record in batch.records]
    )


@router.get("/data")
async def get_time_series_data(
    assetId: str = Query(...),
    dataSourceId: str = Query(...),
    startBusinessDate: date = Query(...),
    endBusinessDate: date = Query(...),
    includeAttributes: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000)
):
    if startBusinessDate >= endBusinessDate:
        raise HTTPException(
            status_code=400,
            detail="startBusinessDate must be before endBusinessDate"
        )

    return await TimeSeriesService.get_time_series_data(
        asset_id=assetId,
        data_source_id=dataSourceId,
        start_business_date=startBusinessDate,
        end_business_date=endBusinessDate,
        include_attributes=includeAttributes,
        limit=limit
    )