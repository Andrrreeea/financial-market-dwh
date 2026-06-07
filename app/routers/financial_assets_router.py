from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    FinancialAssetCreate
)

from app.services.financial_asset_service import (
    FinancialAssetService
)

router = APIRouter(
    prefix="/assets",
    tags=["Financial Assets"]
)


@router.post("/")
async def create_asset(
    asset: FinancialAssetCreate
):
    return await FinancialAssetService.create_asset(
        asset.model_dump()
    )


@router.get("/")
async def get_assets(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    return await FinancialAssetService.get_all_assets(
        offset=offset,
        limit=limit
    )


@router.get("/{asset_id}")
async def get_asset_by_id(asset_id: str):
    asset = await FinancialAssetService.get_asset(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Financial asset not found"
        )

    return asset


@router.put("/{asset_id}")
async def update_asset(
    asset_id: str,
    asset: FinancialAssetCreate
):
    updated_asset = await FinancialAssetService.update_asset(
        asset_id,
        asset.model_dump()
    )

    if updated_asset is None:
        raise HTTPException(
            status_code=404,
            detail="Financial asset not found or already deleted"
        )

    return updated_asset

@router.get("/{asset_id}/history")
async def get_asset_history(asset_id: str):
    history = await FinancialAssetService.get_asset_history(asset_id)

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Financial asset history not found"
        )

    return history

@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    deleted_asset = await FinancialAssetService.delete_asset(asset_id)

    if deleted_asset is None:
        raise HTTPException(
            status_code=404,
            detail="Financial asset not found or already deleted"
        )

    return deleted_asset