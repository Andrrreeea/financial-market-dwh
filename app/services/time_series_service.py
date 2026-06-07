from datetime import datetime, time
from app.database import db


class TimeSeriesService:
    COLLECTION = "time_series_points"

    @staticmethod
    def clean_mongo_document(document):
        if document is None:
            return None

        document["_id"] = str(document["_id"])
        return document

    @staticmethod
    def normalize_business_date(business_date):
        if isinstance(business_date, datetime):
            return business_date

        return datetime.combine(business_date, time.min)

    @staticmethod
    async def ingest_records(records: list):
        now = datetime.utcnow()
        documents = []

        for record in records:
            business_date = TimeSeriesService.normalize_business_date(
                record["business_date"]
            )

            document = {
                "asset_id": record["asset_id"],
                "data_source_id": record["data_source_id"],

                "business_date": business_date,
                "business_date_string": business_date.date().isoformat(),
                "business_year": business_date.year,

                "system_time": now,

                "values": record["values"],
                "attributes": record.get("attributes", {}),

                "is_deleted": False,

                "provenance": {
                    "provider": record["data_source_id"],
                    "source": "api_ingestion",
                    "ingested_at": now.isoformat()
                }
            }

            documents.append(document)

        if not documents:
            return {
                "inserted_count": 0,
                "updated_count": 0,
                "total_processed": 0,
                "records": []
            }

        inserted_count = 0
        updated_count = 0
        processed_records = []

        for document in documents:
            result = await db[TimeSeriesService.COLLECTION].replace_one(
                {
                    "asset_id": document["asset_id"],
                    "data_source_id": document["data_source_id"],
                    "business_date": document["business_date"],
                    "provenance.source": document["provenance"]["source"]
                },
                document,
                upsert=True
            )

            if result.upserted_id:
                inserted_count += 1
            else:
                updated_count += 1

            saved_record = await db[TimeSeriesService.COLLECTION].find_one({
                "asset_id": document["asset_id"],
                "data_source_id": document["data_source_id"],
                "business_date": document["business_date"],
                "provenance.source": document["provenance"]["source"]
            })

            processed_records.append(
                TimeSeriesService.clean_mongo_document(saved_record)
            )

        return {
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "total_processed": len(documents),
            "records": processed_records
        }

    @staticmethod
    async def get_time_series_data(
        asset_id: str,
        data_source_id: str,
        start_business_date,
        end_business_date,
        include_attributes: bool = False,
        limit: int = 100
    ):
        start_datetime = TimeSeriesService.normalize_business_date(
            start_business_date
        )
        end_datetime = TimeSeriesService.normalize_business_date(
            end_business_date
        )

        pipeline = [
            {
                "$match": {
                    "asset_id": asset_id,
                    "data_source_id": data_source_id,
                    "business_date": {
                        "$gte": start_datetime,
                        "$lt": end_datetime
                    },
                    "is_deleted": False
                }
            },
            {
                "$sort": {
                    "business_date": -1,
                    "system_time": -1
                }
            },
            {
                "$group": {
                    "_id": "$business_date",
                    "latest_record": {"$first": "$$ROOT"}
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": "$latest_record"
                }
            },
            {
                "$sort": {
                    "business_date": -1
                }
            },
            {
                "$limit": limit
            }
        ]

        records = await db[TimeSeriesService.COLLECTION].aggregate(
            pipeline
        ).to_list(length=limit)

        cleaned_records = []
        attribute_names = set()

        for record in records:
            record = TimeSeriesService.clean_mongo_document(record)

            if not include_attributes:
                record.pop("attributes", None)
            else:
                for key in record.get("values", {}).keys():
                    attribute_names.add(key)

            cleaned_records.append(record)

        response = {
            "data": {
                "asset_id": asset_id,
                "data_source_id": data_source_id,
                "start_business_date": start_datetime.date().isoformat(),
                "end_business_date": end_datetime.date().isoformat(),
                "returned_records": len(cleaned_records),
                "records": cleaned_records
            }
        }

        if include_attributes:
            response["attributes"] = sorted(list(attribute_names))

        return response