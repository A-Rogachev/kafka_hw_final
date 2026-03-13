from pathlib import Path
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Конфигурация аналитического сервиса"""

    model_config = SettingsConfigDict(case_sensitive=False, env_file=str(CONFIG_DIR / "env.example"), extra="ignore")

    app_name: Final[str] = "Client API"
    api_elasticsearch_index: str = Field("shops_stock_accepted", alias="API_ELASTICSEARCH_INDEX")
    api_ksqldb_url: str = Field(..., alias="API_KSQLDB_URL")
    api_elasticsearch_url: str = Field(..., alias="API_ELASTICSEARCH_URL")
    api_kafka_bootstrap_servers: str = Field(..., alias="API_KAFKA_BOOTSTRAP_SERVERS")
    api_kafka_user_actions_topic_name: str = Field(..., alias="API_KAFKA_USER_ACTIONS_TOPIC_NAME")

    kafka_sasl_mechanism: str = Field(default="PLAIN", alias="KAFKA_SASL_MECHANISM")
    kafka_security_protocol: str = Field(..., alias="KAFKA_SECURITY_PROTOCOL")
    kafka_sasl_username: str = Field(..., alias="KAFKA_SASL_USERNAME")
    kafka_sasl_password: str = Field(..., alias="KAFKA_SASL_PASSWORD")
    kafka_ssl_ca_location: str = Field(..., alias="KAFKA_SSL_CA_LOCATION")


settings = Settings()
