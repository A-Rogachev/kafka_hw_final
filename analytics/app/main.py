import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json, struct, to_json

from src.config import Config, get_config
from src.schemas import product_schema
from src.utils.analytics import analyze_brand_popularity, analyze_category_popularity
from src.utils.recommendations import generate_recommendations

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_spark_session(settings: Config) -> SparkSession:
    return (
        SparkSession.builder.appName(settings.spark_app_name)
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
        .config("spark.executor.memory", "4g")
        .config("spark.executor.cores", 1)
        .config("spark.sql.shuffle.partitions", "3")
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .getOrCreate()
    )


def read_kafka_stream(spark: SparkSession, topic_name: str, kafka_servers: str, settings: Config) -> DataFrame:
    """Чтение данных из Kafka топика"""

    stream_options = {
        "kafka.bootstrap.servers": kafka_servers,
        "subscribe": topic_name,
        "startingOffsets": "earliest",
        "failOnDataLoss": "false",
    }

    if settings.kafka_security_protocol != "PLAINTEXT":
        stream_options["kafka.security.protocol"] = settings.kafka_security_protocol

        if settings.kafka_sasl_mechanism:
            stream_options["kafka.sasl.mechanism"] = settings.kafka_sasl_mechanism
            jaas_config = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="{settings.kafka_sasl_username}" password="{settings.kafka_sasl_password}";'
            stream_options["kafka.sasl.jaas.config"] = jaas_config

        if settings.kafka_ssl_truststore_location:
            stream_options["kafka.ssl.truststore.location"] = settings.kafka_ssl_truststore_location
            stream_options["kafka.ssl.truststore.password"] = settings.kafka_ssl_truststore_password
            stream_options["kafka.ssl.endpoint.identification.algorithm"] = ""

    df = spark.readStream.format("kafka")
    for key, value in stream_options.items():
        df = df.option(key, value)

    return df.load()


def write_to_kafka(df: DataFrame, topic: str, checkpoint_path: str, kafka_servers: str, settings: Config):
    """Запись данных в Kafka топик"""

    write_options = {"kafka.bootstrap.servers": kafka_servers, "topic": topic, "checkpointLocation": checkpoint_path}

    if settings.kafka_security_protocol != "PLAINTEXT":
        write_options["kafka.security.protocol"] = settings.kafka_security_protocol

        if settings.kafka_sasl_mechanism:
            write_options["kafka.sasl.mechanism"] = settings.kafka_sasl_mechanism
            jaas_config = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="{settings.kafka_sasl_username}" password="{settings.kafka_sasl_password}";'
            write_options["kafka.sasl.jaas.config"] = jaas_config

        if settings.kafka_ssl_truststore_location:
            write_options["kafka.ssl.truststore.location"] = settings.kafka_ssl_truststore_location
            write_options["kafka.ssl.truststore.password"] = settings.kafka_ssl_truststore_password
            write_options["kafka.ssl.endpoint.identification.algorithm"] = ""

    writer = df.select(to_json(struct("*")).alias("value")).writeStream.format("kafka")
    for key, value in write_options.items():
        writer = writer.option(key, value)

    return writer.outputMode("update").start()


def write_to_console(df: DataFrame, query_name: str):
    """Запись данных в консоль."""
    return (
        df.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .queryName(query_name)
        .start()
    )


def main() -> None:
    """Запуск сервиса аналитики."""

    logger.info("Starting Product Analytics Service...")

    settings: Config = get_config()
    spark: SparkSession = create_spark_session(settings)
    spark.sparkContext.setLogLevel("WARN")

    raw_stream = read_kafka_stream(
        spark, settings.kafka_analytics_topic_name, settings.kafka_analytics_bootstrap_servers, settings
    )

    logger.info("Kafka stream read successfully.")
    parsed_stream = raw_stream.select(
        from_json(col("value").cast("string"), product_schema).alias("data"), col("timestamp")
    ).select("data.*", "timestamp")
    logger.info("Kafka stream parsed successfully.")

    windowed_stream = parsed_stream.withWatermark("timestamp", settings.watermark_delay)
    logger.info("Windowed stream created successfully.")

    logger.info("Analyzing category popularity...")
    category_stats = analyze_category_popularity(windowed_stream)
    logger.info("Analyzing brand popularity...")
    brand_stats = analyze_brand_popularity(windowed_stream)
    recommendations = generate_recommendations(category_stats, brand_stats)

    logger.info("Writing recommendations")
    write_to_console(category_stats, "category_stats")
    write_to_console(brand_stats, "brand_stats")
    write_to_console(recommendations, "recommendations")
    write_to_kafka(
        recommendations,
        settings.kafka_analytics_topic_name_recommendations,
        f"{settings.checkpoint_location}/recommendations",
        settings.kafka_analytics_bootstrap_servers,
        settings,
    )

    logger.info("Analytics service started successfully. Monitoring streams.")
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
