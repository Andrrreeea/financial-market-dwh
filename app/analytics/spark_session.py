from pyspark.sql import SparkSession


def get_spark_session():
    spark = (
        SparkSession.builder
        .appName("FinancialMarketDWHAnalytics")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")
    return spark