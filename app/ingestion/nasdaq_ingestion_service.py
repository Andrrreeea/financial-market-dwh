from datetime import datetime, time
from uuid import uuid4

import httpx

from app.config import settings
from app.database import db


class NasdaqIngestionService:
    DATA_SOURCE_COLLECTION = "data_sources"
    ASSET_COLLECTION = "financial_assets"
    TIME_SERIES_COLLECTION = "time_series_points"

    BASE_URL = "https://data.nasdaq.com/api/v3/datasets"

    @staticmethod
    def clean_mongo_document(document):
        if document is None:
            return None

        if "_id" in document:
            document["_id"] = str(document["_id"])

        return document

    @staticmethod
    async def ensure_nasdaq_data_source():
        existing = await db[NasdaqIngestionService.DATA_SOURCE_COLLECTION].find_one({
            "name": "Nasdaq Data Link"
        })

        if existing:
            return existing["data_source_id"]

        now = datetime.utcnow()

        data_source = {
            "data_source_id": str(uuid4()),
            "name": "Nasdaq Data Link",
            "provider_type": "external_api",
            "base_url": "https://data.nasdaq.com/api/v3",
            "description": "External financial data provider used for real market data ingestion.",
            "license": "Nasdaq Data Link account/API key",
            "additional_attributes": {
                "api_type": "REST",
                "supports_time_series": True,
                "provider": "Nasdaq"
            },
            "created_at": now,
            "provenance": {
                "created_by": "system",
                "source": "nasdaq_ingestion",
                "created_at": now.isoformat()
            }
        }

        result = await db[NasdaqIngestionService.DATA_SOURCE_COLLECTION].insert_one(
            data_source
        )

        created = await db[NasdaqIngestionService.DATA_SOURCE_COLLECTION].find_one({
            "_id": result.inserted_id
        })

        return created["data_source_id"]

    @staticmethod
    async def ensure_asset(symbol: str, dataset_code: str, asset_class: str = "stock"):
        existing = await db[NasdaqIngestionService.ASSET_COLLECTION].find_one({
            "symbol": symbol,
            "is_current": True,
            "is_deleted": False
        })

        if existing:
            return existing["asset_id"]

        now = datetime.utcnow()

        asset = {
            "asset_id": str(uuid4()),
            "symbol": symbol,
            "name": symbol,
            "asset_class": asset_class,
            "description": f"Financial instrument imported from Nasdaq Data Link dataset {dataset_code}.",
            "region": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "additional_attributes": {
                "nasdaq_dataset_code": dataset_code
            },
            "version": 1,
            "valid_from": now,
            "valid_to": None,
            "is_current": True,
            "is_deleted": False,
            "created_at": now,
            "provenance": {
                "created_by": "system",
                "source": "nasdaq_ingestion",
                "dataset_code": dataset_code,
                "created_at": now.isoformat()
            }
        }

        result = await db[NasdaqIngestionService.ASSET_COLLECTION].insert_one(asset)

        created = await db[NasdaqIngestionService.ASSET_COLLECTION].find_one({
            "_id": result.inserted_id
        })

        return created["asset_id"]

    @staticmethod
    def map_nasdaq_row_to_internal_record(
        row: list,
        columns: list,
        asset_id: str,
        data_source_id: str,
        dataset_code: str
    ):
        row_dict = dict(zip(columns, row))

        date_value = row_dict.get("Date")

        if date_value is None:
            raise ValueError("Nasdaq row does not contain a Date column.")

        business_date = datetime.combine(
            datetime.strptime(date_value, "%Y-%m-%d").date(),
            time.min
        )

        values = {}

        for key, value in row_dict.items():
            if key == "Date":
                continue

            if value is None:
                continue

            normalized_key = key.strip().lower().replace(" ", "_")

            try:
                values[normalized_key] = float(value)
            except (TypeError, ValueError):
                values[normalized_key] = value

        now = datetime.utcnow()

        return {
            "asset_id": asset_id,
            "data_source_id": data_source_id,
            "business_date": business_date,
            "business_date_string": business_date.date().isoformat(),
            "business_year": business_date.year,
            "system_time": now,
            "values": values,
            "attributes": {
                "provider": "Nasdaq Data Link",
                "dataset_code": dataset_code,
                "original_columns": columns
            },
            "is_deleted": False,
            "provenance": {
                "provider": "Nasdaq Data Link",
                "dataset_code": dataset_code,
                "source": "external_api",
                "ingested_at": now.isoformat()
            }
        }

    @staticmethod
    async def ingest_dataset(
        dataset_code: str,
        symbol: str,
        start_date: str,
        end_date: str,
        asset_class: str = "stock"
    ):
        if not settings.NASDAQ_API_KEY:
            raise ValueError("NASDAQ_API_KEY is missing from .env")

        data_source_id = await NasdaqIngestionService.ensure_nasdaq_data_source()
        asset_id = await NasdaqIngestionService.ensure_asset(
            symbol=symbol,
            dataset_code=dataset_code,
            asset_class=asset_class
        )

        url = f"{NasdaqIngestionService.BASE_URL}/{dataset_code}.json"

        params = {
            "api_key": settings.NASDAQ_API_KEY,
            "start_date": start_date,
            "end_date": end_date,
            "order": "asc"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        dataset = payload.get("dataset", {})
        columns = dataset.get("column_names", [])
        rows = dataset.get("data", [])

        transformed_records = []

        for row in rows:
            transformed_records.append(
                NasdaqIngestionService.map_nasdaq_row_to_internal_record(
                    row=row,
                    columns=columns,
                    asset_id=asset_id,
                    data_source_id=data_source_id,
                    dataset_code=dataset_code
                )
            )

        if not transformed_records:
            return {
                "status": "no_data",
                "message": "Nasdaq returned no records for the selected dataset and date interval.",
                "dataset_code": dataset_code,
                "symbol": symbol
            }

        insert_result = await db[NasdaqIngestionService.TIME_SERIES_COLLECTION].insert_many(
            transformed_records
        )

        return {
            "status": "success",
            "provider": "Nasdaq Data Link",
            "dataset_code": dataset_code,
            "symbol": symbol,
            "asset_id": asset_id,
            "data_source_id": data_source_id,
            "requested_interval": {
                "start_date": start_date,
                "end_date": end_date
            },
            "extracted_records": len(rows),
            "loaded_records": len(insert_result.inserted_ids),
            "provenance": {
                "api_url": url,
                "source": "external_api",
                "provider": "Nasdaq Data Link",
                "dataset_code": dataset_code,
                "ingested_at": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    async def ingest_datatable(
        table_code: str,
        symbol: str,
        start_date: str,
        end_date: str,
        asset_class: str = "stock",
        ticker: str | None = None
    ):
        if not settings.NASDAQ_API_KEY:
            raise ValueError("NASDAQ_API_KEY is missing from .env")

        data_source_id = await NasdaqIngestionService.ensure_nasdaq_data_source()

        asset_id = await NasdaqIngestionService.ensure_asset(
            symbol=symbol,
            dataset_code=table_code,
            asset_class=asset_class
        )

        url = f"https://data.nasdaq.com/api/v3/datatables/{table_code}.json"

        params = {
            "api_key": settings.NASDAQ_API_KEY,
            "date.gte": start_date,
            "date.lte": end_date
        }

        if ticker:
            params["ticker"] = ticker

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        datatable = payload.get("datatable", {})
        columns_metadata = datatable.get("columns", [])
        rows = datatable.get("data", [])

        column_names = [
            column["name"]
            for column in columns_metadata
        ]

        transformed_records = []

        for row in rows:
            row_dict = dict(zip(column_names, row))

            date_value = row_dict.get("date")

            if not date_value:
                continue

            business_date = datetime.combine(
                datetime.strptime(date_value, "%Y-%m-%d").date(),
                time.min
            )

            values = {}

            for key, value in row_dict.items():
                if key in ["date", "ticker"]:
                    continue

                if value is None:
                    continue

                normalized_key = key.strip().lower().replace(" ", "_")

                try:
                    values[normalized_key] = float(value)
                except (TypeError, ValueError):
                    values[normalized_key] = value

            record = {
                "asset_id": asset_id,
                "data_source_id": data_source_id,
                "business_date": business_date,
                "business_date_string": business_date.date().isoformat(),
                "business_year": business_date.year,
                "system_time": datetime.utcnow(),
                "values": values,
                "attributes": {
                    "provider": "Nasdaq Data Link",
                    "table_code": table_code,
                    "ticker": row_dict.get("ticker"),
                    "original_columns": column_names
                },
                "is_deleted": False,
                "provenance": {
                    "provider": "Nasdaq Data Link",
                    "table_code": table_code,
                    "source": "external_api_datatable",
                    "api_endpoint": url,
                    "query_params": {
                        "date.gte": start_date,
                        "date.lte": end_date,
                        "ticker": ticker
                    },
                    "ingested_at": datetime.utcnow().isoformat()
                }
            }

            transformed_records.append(record)

        if not transformed_records:
            return {
                "status": "no_data",
                "message": "Nasdaq Data Link returned no rows for the selected table and filters.",
                "table_code": table_code,
                "symbol": symbol
            }

        insert_result = await db[
            NasdaqIngestionService.TIME_SERIES_COLLECTION
        ].insert_many(transformed_records)

        return {
            "status": "success",
            "provider": "Nasdaq Data Link",
            "api_type": "datatables",
            "table_code": table_code,
            "symbol": symbol,
            "asset_id": asset_id,
            "data_source_id": data_source_id,
            "requested_interval": {
                "start_date": start_date,
                "end_date": end_date
            },
            "filters": {
                "ticker": ticker
            },
            "extracted_records": len(rows),
            "loaded_records": len(insert_result.inserted_ids),
            "provenance": {
                "api_url": url,
                "source": "external_api_datatable",
                "provider": "Nasdaq Data Link",
                "table_code": table_code,
                "ingested_at": datetime.utcnow().isoformat()
            }
        }