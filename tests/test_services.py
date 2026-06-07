import pytest
from datetime import date

from app.services.financial_asset_service import FinancialAssetService
from app.services.time_series_service import TimeSeriesService


@pytest.mark.asyncio
async def test_create_asset_returns_versioned_current_asset():
    asset_data = {
        "symbol": "UNIT_TEST_ASSET",
        "name": "Unit Test Asset",
        "asset_class": "stock",
        "description": "Test asset",
        "region": "US",
        "currency": "USD",
        "exchange": "TEST",
        "additional_attributes": {"test": True}
    }

    asset = await FinancialAssetService.create_asset(asset_data)

    assert asset["symbol"] == "UNIT_TEST_ASSET"
    assert asset["version"] == 1
    assert asset["is_current"] is True
    assert asset["is_deleted"] is False
    assert "provenance" in asset


@pytest.mark.asyncio
async def test_update_asset_creates_new_temporal_version():
    asset = await FinancialAssetService.create_asset({
        "symbol": "UNIT_TEST_UPDATE",
        "name": "Before Update",
        "asset_class": "stock",
        "description": "Before",
        "region": "US",
        "currency": "USD",
        "exchange": "TEST",
        "additional_attributes": {}
    })

    updated = await FinancialAssetService.update_asset(
        asset["asset_id"],
        {
            "symbol": "UNIT_TEST_UPDATE",
            "name": "After Update",
            "asset_class": "stock",
            "description": "After",
            "region": "US",
            "currency": "USD",
            "exchange": "TEST",
            "additional_attributes": {"updated": True}
        }
    )

    history = await FinancialAssetService.get_asset_history(asset["asset_id"])

    assert updated["version"] == 2
    assert updated["name"] == "After Update"
    assert len(history) == 2
    assert history[0]["is_current"] is False
    assert history[1]["is_current"] is True


@pytest.mark.asyncio
async def test_delete_asset_creates_temporal_delete_marker():
    asset = await FinancialAssetService.create_asset({
        "symbol": "UNIT_TEST_DELETE",
        "name": "Delete Test",
        "asset_class": "stock",
        "description": "Delete test",
        "region": "US",
        "currency": "USD",
        "exchange": "TEST",
        "additional_attributes": {}
    })

    deleted = await FinancialAssetService.delete_asset(asset["asset_id"])
    history = await FinancialAssetService.get_asset_history(asset["asset_id"])

    assert deleted["is_deleted"] is True
    assert deleted["is_current"] is True
    assert deleted["version"] == 2
    assert len(history) == 2
    assert history[-1]["provenance"]["operation"] == "temporal_delete"


@pytest.mark.asyncio
async def test_get_all_assets_supports_pagination():
    result = await FinancialAssetService.get_all_assets(offset=0, limit=1)

    assert "offset" in result
    assert "limit" in result
    assert "total" in result
    assert "items" in result
    assert result["limit"] == 1
    assert len(result["items"]) <= 1


@pytest.mark.asyncio
async def test_time_series_ingestion_is_idempotent():
    records = [
        {
            "asset_id": "UNIT_TEST_ASSET_ID",
            "data_source_id": "UNIT_TEST_SOURCE_ID",
            "business_date": date(2025, 1, 1),
            "values": {
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000
            },
            "attributes": {
                "currency": "USD",
                "frequency": "daily"
            }
        }
    ]

    first_run = await TimeSeriesService.ingest_records(records)
    second_run = await TimeSeriesService.ingest_records(records)

    assert first_run["total_processed"] == 1
    assert second_run["total_processed"] == 1
    assert second_run["inserted_count"] == 0
    assert second_run["updated_count"] == 1