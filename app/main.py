from fastapi import FastAPI
from app.config import settings
from app.database import db
from app.analytics.spark_session import get_spark_session
from app.routers.financial_assets_router import router as assets_router
from app.routers.data_sources_router import router as data_sources_router
from app.routers.time_series_router import router as time_series_router
from app.routers.analytics_router import router as analytics_router
from app.routers.ingestion_router import router as ingestion_router
from app.config import settings

print("NASDAQ KEY LOADED:", bool(settings.NASDAQ_API_KEY))

app = FastAPI(
    title=settings.APP_NAME,
    description="Financial Market Data Warehouse with MongoDB, temporal versioning, provenance tracking, PySpark analytics and MCP support.",
    version="1.0.0"
)
app.include_router(assets_router)
app.include_router(data_sources_router)
app.include_router(time_series_router)
app.include_router(analytics_router)
app.include_router(ingestion_router)

@app.get("/")
async def root():
    return {
        "message": "Financial Market Data Warehouse API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    collections = await db.list_collection_names()
    return {
        "status": "healthy",
        "database": settings.DATABASE_NAME,
        "collections": collections
    }


@app.get("/spark-test")
async def spark_test():
    spark = get_spark_session()

    data = [
        ("AAPL", 190.5),
        ("MSFT", 410.2),
        ("BTC", 65000.0)
    ]

    df = spark.createDataFrame(data, ["symbol", "price"])
    result = df.collect()

    return {
        "status": "PySpark is working",
        "data": [{"symbol": row["symbol"], "price": row["price"]} for row in result]
    }