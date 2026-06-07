import httpx
from mcp.server.fastmcp import FastMCP


API_BASE_URL = "http://127.0.0.1:8000"

mcp = FastMCP("Financial Market Data Warehouse MCP Server")


async def api_get(path: str, params: dict | None = None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{API_BASE_URL}{path}",
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_assets(offset: int = 0, limit: int = 20):
    """
    List available financial assets from the warehouse.
    Returns a paginated list of current, non-deleted assets.
    """
    return await api_get(
        "/assets/",
        params={
            "offset": offset,
            "limit": limit
        }
    )


@mcp.tool()
async def get_asset_details(asset_id: str):
    """
    Get the latest current version of a financial asset by asset_id.
    """
    return await api_get(f"/assets/{asset_id}")


@mcp.tool()
async def get_asset_history(asset_id: str):
    """
    Get all temporal versions of a financial asset.
    Useful for explaining historical changes.
    """
    return await api_get(f"/assets/{asset_id}/history")


@mcp.tool()
async def list_data_sources(offset: int = 0, limit: int = 20):
    """
    List available financial data sources from the warehouse.
    Returns paginated source metadata.
    """
    return await api_get(
        "/data-sources/",
        params={
            "offset": offset,
            "limit": limit
        }
    )


@mcp.tool()
async def get_data_source_details(data_source_id: str):
    """
    Get detailed metadata about a financial data source.
    """
    return await api_get(f"/data-sources/{data_source_id}")


@mcp.tool()
async def get_time_series_data(
    asset_id: str,
    data_source_id: str,
    start_business_date: str,
    end_business_date: str,
    include_attributes: bool = False,
    limit: int = 100
):
    """
    Get time-series records for an asset and data source in a bounded interval.
    Dates must use YYYY-MM-DD format.
    The interval is [start_business_date, end_business_date).
    Results are returned newest-first.
    """
    return await api_get(
        "/data",
        params={
            "assetId": asset_id,
            "dataSourceId": data_source_id,
            "startBusinessDate": start_business_date,
            "endBusinessDate": end_business_date,
            "includeAttributes": include_attributes,
            "limit": limit
        }
    )


@mcp.tool()
async def get_analytics_aggregations(limit: int = 20):
    """
    Get persisted PySpark aggregation results.
    Includes yearly count, min, max and average close price.
    """
    return await api_get(
        "/analytics/aggregations",
        params={
            "limit": limit
        }
    )


@mcp.tool()
async def get_predictions(limit: int = 20):
    """
    Get persisted Spark ML close-price prediction results.
    """
    return await api_get(
        "/analytics/predictions",
        params={
            "limit": limit
        }
    )


if __name__ == "__main__":
    mcp.run()