from datetime import datetime
from uuid import uuid4

from app.database import db


class FinancialAssetService:
    COLLECTION = "financial_assets"

    @staticmethod
    def clean_mongo_document(document):
        if document is None:
            return None

        document["_id"] = str(document["_id"])
        return document

    @staticmethod
    async def create_asset(asset_data: dict):
        now = datetime.utcnow()

        asset = {
            "asset_id": str(uuid4()),
            "symbol": asset_data["symbol"],
            "name": asset_data["name"],
            "asset_class": asset_data["asset_class"],
            "description": asset_data.get("description"),
            "region": asset_data.get("region"),
            "currency": asset_data.get("currency"),
            "exchange": asset_data.get("exchange"),
            "additional_attributes": asset_data.get("additional_attributes", {}),

            "version": 1,
            "valid_from": now,
            "valid_to": None,
            "is_current": True,
            "is_deleted": False,
            "created_at": now,

            "provenance": {
                "created_by": "system",
                "source": "api",
                "created_at": now.isoformat()
            }
        }

        result = await db[FinancialAssetService.COLLECTION].insert_one(asset)

        created_asset = await db[FinancialAssetService.COLLECTION].find_one(
            {"_id": result.inserted_id}
        )

        return FinancialAssetService.clean_mongo_document(created_asset)

    @staticmethod
    async def get_all_assets(offset: int = 0, limit: int = 20):
        cursor = (
            db[FinancialAssetService.COLLECTION]
            .find({
                "is_current": True,
                "is_deleted": False
            })
            .sort("symbol", 1)
            .skip(offset)
            .limit(limit)
        )

        assets = await cursor.to_list(length=limit)

        total = await db[FinancialAssetService.COLLECTION].count_documents({
            "is_current": True,
            "is_deleted": False
        })

        return {
            "offset": offset,
            "limit": limit,
            "total": total,
            "items": [
                FinancialAssetService.clean_mongo_document(asset)
                for asset in assets
            ]
        }

    @staticmethod
    async def get_asset(asset_id: str):
        asset = await db[FinancialAssetService.COLLECTION].find_one({
            "asset_id": asset_id,
            "is_current": True
        })

        return FinancialAssetService.clean_mongo_document(asset)

    @staticmethod
    async def update_asset(asset_id: str, updated_data: dict):
        now = datetime.utcnow()

        current_asset = await db[FinancialAssetService.COLLECTION].find_one({
            "asset_id": asset_id,
            "is_current": True,
            "is_deleted": False
        })

        if current_asset is None:
            return None

        await db[FinancialAssetService.COLLECTION].update_one(
            {"_id": current_asset["_id"]},
            {
                "$set": {
                    "is_current": False,
                    "valid_to": now
                }
            }
        )

        new_asset_version = {
            "asset_id": current_asset["asset_id"],
            "symbol": updated_data.get("symbol", current_asset["symbol"]),
            "name": updated_data.get("name", current_asset["name"]),
            "asset_class": updated_data.get("asset_class", current_asset["asset_class"]),
            "description": updated_data.get("description", current_asset.get("description")),
            "region": updated_data.get("region", current_asset.get("region")),
            "currency": updated_data.get("currency", current_asset.get("currency")),
            "exchange": updated_data.get("exchange", current_asset.get("exchange")),
            "additional_attributes": updated_data.get(
                "additional_attributes",
                current_asset.get("additional_attributes", {})
            ),

            "version": current_asset["version"] + 1,
            "valid_from": now,
            "valid_to": None,
            "is_current": True,
            "is_deleted": False,
            "created_at": now,

            "provenance": {
                "created_by": "system",
                "source": "api",
                "operation": "temporal_update",
                "previous_version": current_asset["version"],
                "updated_at": now.isoformat()
            }
        }

        result = await db[FinancialAssetService.COLLECTION].insert_one(
            new_asset_version
        )

        created_version = await db[FinancialAssetService.COLLECTION].find_one(
            {"_id": result.inserted_id}
        )

        return FinancialAssetService.clean_mongo_document(created_version)

    @staticmethod
    async def get_asset_history(asset_id: str):
        cursor = (
            db[FinancialAssetService.COLLECTION]
            .find({"asset_id": asset_id})
            .sort("version", 1)
        )

        history = await cursor.to_list(length=None)

        return [
            FinancialAssetService.clean_mongo_document(asset)
            for asset in history
        ]

    @staticmethod
    async def delete_asset(asset_id: str):
        now = datetime.utcnow()

        current_asset = await db[FinancialAssetService.COLLECTION].find_one({
            "asset_id": asset_id,
            "is_current": True,
            "is_deleted": False
        })

        if current_asset is None:
            return None

        await db[FinancialAssetService.COLLECTION].update_one(
            {"_id": current_asset["_id"]},
            {
                "$set": {
                    "is_current": False,
                    "valid_to": now
                }
            }
        )

        deletion_marker = {
            "asset_id": current_asset["asset_id"],
            "symbol": current_asset["symbol"],
            "name": current_asset["name"],
            "asset_class": current_asset["asset_class"],
            "description": current_asset.get("description"),
            "region": current_asset.get("region"),
            "currency": current_asset.get("currency"),
            "exchange": current_asset.get("exchange"),
            "additional_attributes": current_asset.get("additional_attributes", {}),

            "version": current_asset["version"] + 1,
            "valid_from": now,
            "valid_to": None,
            "is_current": True,
            "is_deleted": True,
            "deleted_from": now,
            "created_at": now,

            "provenance": {
                "created_by": "system",
                "source": "api",
                "operation": "temporal_delete",
                "previous_version": current_asset["version"],
                "deleted_at": now.isoformat()
            }
        }

        result = await db[FinancialAssetService.COLLECTION].insert_one(
            deletion_marker
        )

        created_marker = await db[FinancialAssetService.COLLECTION].find_one(
            {"_id": result.inserted_id}
        )

        return FinancialAssetService.clean_mongo_document(created_marker)