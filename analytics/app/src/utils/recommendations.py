from pyspark.sql import DataFrame
from pyspark.sql.functions import col, current_timestamp, lit


def generate_recommendations(category_stats: DataFrame, brand_stats: DataFrame) -> DataFrame:
    """
    Генерация рекомендаций на основе аналитики.

    Создает рекомендации:
    - ВСЕ категории (топ-N выбирается в ksqlDB)
    - ВСЕ бренды (топ-N выбирается в ksqlDB)
    """
    top_categories = (
        category_stats.withColumn("recommendation_type", lit("top_category"))  # Убрали .limit(5)
        .withColumn("recommendation_score", col("product_count").cast("double"))
        .select(
            col("category").alias("item_id"),
            col("recommendation_type"),
            col("recommendation_score"),
            col("product_count"),
            col("avg_price"),
            current_timestamp().alias("generated_at"),
        )
    )
    top_brands = (
        brand_stats.withColumn("recommendation_type", lit("top_brand"))  # Убрали .limit(5)
        .withColumn("recommendation_score", col("product_count").cast("double"))
        .select(
            col("brand").alias("item_id"),
            col("recommendation_type"),
            col("recommendation_score"),
            col("product_count"),
            col("avg_price"),
            current_timestamp().alias("generated_at"),
        )
    )
    return top_categories.union(top_brands)
