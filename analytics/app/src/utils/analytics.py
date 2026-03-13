from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, count
from pyspark.sql.functions import sum as spark_sum


def analyze_category_popularity(df: DataFrame) -> DataFrame:
    """
    Анализ популярности категорий товаров.

    Подсчитывает количество товаров и среднюю цену по каждой категории.
    """
    return df.groupBy("category").agg(
        count("product_id").alias("product_count"),
        avg("price.amount").alias("avg_price"),
        spark_sum("stock.available").alias("total_stock"),
    )


def analyze_brand_popularity(df: DataFrame) -> DataFrame:
    """Анализ популярности брендов"""
    return df.groupBy("brand").agg(count("product_id").alias("product_count"), avg("price.amount").alias("avg_price"))


def analyze_price_segments(df: DataFrame) -> DataFrame:
    """Анализ ценовых сегментов"""
    return df.groupBy((col("price.amount") / 1000).cast("int").alias("price_segment_k")).agg(
        count("product_id").alias("product_count"), avg("price.amount").alias("avg_price")
    )
