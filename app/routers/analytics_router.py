from app.analytics.spark_analytics_service import SparkAnalyticsService
from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/analytics",
    tags=["PySpark Analytics"]
)


@router.post("/yearly-aggregation")
async def run_yearly_aggregation():
    return await SparkAnalyticsService.run_yearly_aggregation()

@router.post("/predict-close")
async def run_close_price_prediction():
    return await SparkAnalyticsService.run_close_price_prediction()

@router.get("/aggregations")
async def get_aggregations(
    limit: int = Query(20, ge=1, le=100)
):
    return await SparkAnalyticsService.get_aggregations(limit=limit)


@router.get("/predictions")
async def get_predictions(
    limit: int = Query(20, ge=1, le=100)
):
    return await SparkAnalyticsService.get_predictions(limit=limit)