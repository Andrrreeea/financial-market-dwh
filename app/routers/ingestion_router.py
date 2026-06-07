from fastapi import APIRouter, HTTPException, Query

from app.ingestion.nasdaq_ingestion_service import NasdaqIngestionService


router = APIRouter(
    prefix="/ingestion",
    tags=["External Data Ingestion"]
)


@router.post("/nasdaq")
async def ingest_nasdaq_dataset(
    dataset_code: str = Query(..., description="Nasdaq dataset code, e.g. WIKI/AAPL or EOD/AAPL"),
    symbol: str = Query(..., description="Internal asset symbol, e.g. AAPL"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    asset_class: str = Query("stock")
):
    try:
        return await NasdaqIngestionService.ingest_dataset(
            dataset_code=dataset_code,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            asset_class=asset_class
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception)
        )
    
@router.post("/nasdaq-datatable")
async def ingest_nasdaq_datatable(
    table_code: str = Query(..., description="Nasdaq table code, e.g. NDAQ/RTAT10"),
    symbol: str = Query(..., description="Internal asset symbol, e.g. AAPL_RTAT"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    asset_class: str = Query("stock"),
    ticker: str | None = Query(None, description="Optional ticker filter, e.g. AAPL")
):
    try:
        return await NasdaqIngestionService.ingest_datatable(
            table_code=table_code,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            asset_class=asset_class,
            ticker=ticker
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception)
        )