from datetime import datetime
from uuid import uuid4

from app.database import db


class DataSourceService:
    COLLECTION = "data_sources"

    @staticmethod
    def clean_mongo_document(document):
        if document is None:
            return None

        document["_id"] = str(document["_id"])
        return document

    @staticmethod
    async def create_data_source(data_source_data: dict):
        now = datetime.utcnow()

        data_source = {
            "data_source_id": str(uuid4()),
            "name": data_source_data["name"],
            "provider_type": data_source_data["provider_type"],
            "base_url": data_source_data.get("base_url"),
            "description": data_source_data.get("description"),
            "license": data_source_data.get("license"),
            "additional_attributes": data_source_data.get("additional_attributes", {}),

            "created_at": now,

            "provenance": {
                "created_by": "system",
                "source": "api",
                "created_at": now.isoformat()
            }
        }

        result = await db[DataSourceService.COLLECTION].insert_one(data_source)

        created_data_source = await db[DataSourceService.COLLECTION].find_one(
            {"_id": result.inserted_id}
        )

        return DataSourceService.clean_mongo_document(created_data_source)

    @staticmethod
    async def get_all_data_sources(offset: int = 0, limit: int = 20):
        cursor = (
            db[DataSourceService.COLLECTION]
            .find()
            .sort("name", 1)
            .skip(offset)
            .limit(limit)
        )

        data_sources = await cursor.to_list(length=limit)

        total = await db[DataSourceService.COLLECTION].count_documents({})

        return {
            "offset": offset,
            "limit": limit,
            "total": total,
            "items": [
                DataSourceService.clean_mongo_document(source)
                for source in data_sources
            ]
        }

    @staticmethod
    async def get_data_source(data_source_id: str):
        data_source = await db[DataSourceService.COLLECTION].find_one({
            "data_source_id": data_source_id
        })

        return DataSourceService.clean_mongo_document(data_source)