from datetime import datetime
from app.database import db
from app.analytics.spark_session import get_spark_session
from pyspark.sql.functions import avg, min, max, count
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

class SparkAnalyticsService:

    SOURCE_COLLECTION = "time_series_points"
    AGGREGATION_COLLECTION = "analytics_aggregations"

    PREDICTION_COLLECTION = "analytics_predictions"

    @staticmethod
    async def get_aggregations(limit: int = 20):
        cursor = (
            db[SparkAnalyticsService.AGGREGATION_COLLECTION]
            .find()
            .sort("computed_at", -1)
            .limit(limit)
        )

        results = await cursor.to_list(length=limit)

        return {
            "total_returned": len(results),
            "items": [
                SparkAnalyticsService.clean_mongo_document(item)
                for item in results
            ]
        }

    @staticmethod
    async def get_predictions(limit: int = 20):
        cursor = (
            db[SparkAnalyticsService.PREDICTION_COLLECTION]
            .find()
            .sort("computed_at", -1)
            .limit(limit)
        )

        results = await cursor.to_list(length=limit)

        return {
            "total_returned": len(results),
            "items": [
                SparkAnalyticsService.clean_mongo_document(item)
                for item in results
            ]
        }

    @staticmethod
    async def run_close_price_prediction():
        records = await db[SparkAnalyticsService.SOURCE_COLLECTION].find({
            "is_deleted": False
        }).to_list(length=None)

        if not records:
            return {
                "status": "no_data",
                "message": "No time series records found."
            }

        spark_input = []

        for record in records:
            values = record.get("values", {})

            required_fields = ["open", "high", "low", "close", "volume"]

            if not all(field in values for field in required_fields):
                continue

            spark_input.append({
                "asset_id": record["asset_id"],
                "data_source_id": record["data_source_id"],
                "business_date": record["business_date_string"],
                "open": float(values["open"]),
                "high": float(values["high"]),
                "low": float(values["low"]),
                "volume": float(values["volume"]),
                "close": float(values["close"])
            })

        if len(spark_input) < 3:
            return {
                "status": "not_enough_data",
                "message": "At least 3 valid records are required for prediction."
            }

        spark = get_spark_session()

        df = spark.createDataFrame(spark_input)

        assembler = VectorAssembler(
            inputCols=["open", "high", "low", "volume"],
            outputCol="features"
        )

        prepared_df = assembler.transform(df)

        lr = LinearRegression(
            featuresCol="features",
            labelCol="close",
            predictionCol="predicted_close",
            maxIter=10,
            regParam=0.1
        )

        model = lr.fit(prepared_df)

        predictions_df = model.transform(prepared_df)

        rows = predictions_df.select(
            "asset_id",
            "data_source_id",
            "business_date",
            "open",
            "high",
            "low",
            "volume",
            "close",
            "predicted_close"
        ).collect()

        now = datetime.utcnow()

        documents = []

        for row in rows:
            documents.append({
                "asset_id": row["asset_id"],
                "data_source_id": row["data_source_id"],
                "business_date": row["business_date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": float(row["volume"]),
                "actual_close": float(row["close"]),
                "predicted_close": float(row["predicted_close"]),
                "computed_at": now,
                "engine": "pyspark_ml",
                "workflow": "linear_regression_close_prediction"
            })

        result = await db[SparkAnalyticsService.PREDICTION_COLLECTION].insert_many(
            documents
        )

        inserted_documents = await db[
            SparkAnalyticsService.PREDICTION_COLLECTION
        ].find({
            "_id": {"$in": result.inserted_ids}
        }).to_list(length=None)

        cleaned_results = [
            SparkAnalyticsService.clean_mongo_document(document)
            for document in inserted_documents
        ]

        return {
            "status": "success",
            "workflow": "linear_regression_close_prediction",
            "training_records": len(spark_input),
            "inserted_count": len(cleaned_results),
            "results": cleaned_results
        }

    @staticmethod
    def clean_mongo_document(document):
        if document is None:
            return None

        if "_id" in document:
            document["_id"] = str(document["_id"])

        return document

    @staticmethod
    async def run_yearly_aggregation():
        records = await db[SparkAnalyticsService.SOURCE_COLLECTION].find({
            "is_deleted": False
        }).to_list(length=None)

        if not records:
            return {
                "status": "no_data",
                "message": "No time series records found."
            }

        spark_input = []

        for record in records:
            values = record.get("values", {})

            if "close" not in values:
                continue

            spark_input.append({
                "asset_id": record["asset_id"],
                "data_source_id": record["data_source_id"],
                "business_year": int(record["business_year"]),
                "close": float(values["close"])
            })

        if not spark_input:
            return {
                "status": "no_valid_data",
                "message": "No records with close value found."
            }

        spark = get_spark_session()
        df = spark.createDataFrame(spark_input)

        result_df = (
            df.groupBy(
                "asset_id",
                "data_source_id",
                "business_year"
            )
            .agg(
                count("close").alias("record_count"),
                min("close").alias("min_close"),
                max("close").alias("max_close"),
                avg("close").alias("avg_close")
            )
)

        rows = result_df.collect()
        now = datetime.utcnow()

        documents = []

        for row in rows:
            documents.append({
                "asset_id": row["asset_id"],
                "data_source_id": row["data_source_id"],
                "business_year": row["business_year"],
                "record_count": int(row["record_count"]),
                "min_close": float(row["min_close"]),
                "max_close": float(row["max_close"]),
                "avg_close": float(row["avg_close"]),
                "computed_at": now,
                "engine": "pyspark",
                "workflow": "yearly_aggregation"
            })

        result = await db[SparkAnalyticsService.AGGREGATION_COLLECTION].insert_many(
            documents
        )

        inserted_documents = await db[SparkAnalyticsService.AGGREGATION_COLLECTION].find({
            "_id": {"$in": result.inserted_ids}
        }).to_list(length=None)

        cleaned_results = [
            SparkAnalyticsService.clean_mongo_document(document)
            for document in inserted_documents
        ]

        return {
            "status": "success",
            "workflow": "yearly_aggregation",
            "inserted_count": len(cleaned_results),
            "results": cleaned_results
        }