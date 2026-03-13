from pyspark.sql.types import ArrayType, DoubleType, IntegerType, StringType, StructField, StructType

product_schema = StructType(
    [
        StructField("product_id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("description", StringType(), True),
        StructField(
            "price",
            StructType([StructField("amount", DoubleType(), True), StructField("currency", StringType(), True)]),
            True,
        ),
        StructField("category", StringType(), True),
        StructField("brand", StringType(), True),
        StructField(
            "stock",
            StructType([StructField("available", IntegerType(), True), StructField("reserved", IntegerType(), True)]),
            True,
        ),
        StructField("sku", StringType(), True),
        StructField("tags", ArrayType(StringType()), True),
        StructField("store_id", StringType(), True),
        StructField("created_at", StringType(), True),
        StructField("updated_at", StringType(), True),
    ]
)
