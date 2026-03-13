from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[2]


class Config(BaseSettings):
    """Конфигурация аналитического сервиса"""

    model_config = SettingsConfigDict(case_sensitive=False, env_file=str(CONFIG_DIR / "env.example"), extra="ignore")

    kafka_analytics_bootstrap_servers: str = Field(..., alias="KAFKA_ANALYTICS_BOOTSTRAP_SERVERS")
    kafka_analytics_topic_name: str = Field(..., alias="KAFKA_ANALYTICS_TOPIC_NAME")
    kafka_analytics_topic_name_recommendations: str = Field(..., alias="KAFKA_ANALYTICS_TOPIC_NAME_RECOMMENDATIONS")
    spark_app_name: str = "ProductAnalytics"
    checkpoint_location: str = "/tmp/spark-checkpoints"
    window_duration: str = "1 minutes"
    watermark_delay: str = "10 minutes"

    kafka_sasl_mechanism: str = Field(default="PLAIN", alias="KAFKA_SASL_MECHANISM")
    kafka_security_protocol: str = Field(default="PLAINTEXT", alias="KAFKA_SECURITY_PROTOCOL")
    kafka_sasl_username: str = Field(..., alias="KAFKA_SASL_USERNAME")
    kafka_sasl_password: str = Field(..., alias="KAFKA_SASL_PASSWORD")
    kafka_ssl_truststore_location: str = Field(..., alias="KAFKA_SSL_TRUSTSTORE_LOCATION")
    kafka_ssl_truststore_password: str = Field(..., alias="KAFKA_SSL_TRUSTSTORE_PASSWORD")


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
