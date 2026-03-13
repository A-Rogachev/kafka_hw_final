from pathlib import Path
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[3]

DEFAULT_PRODUCER_RETRIES: Final[int] = 3
DEFAULT_PRODUCER_ACKS: Final[str] = "all"
DEFAULT_POLL_TIMEOUT_SECONDS: Final[float] = 0.1
DEFAULT_LOG_LEVEL: Final[int] = 1


class ProducerSettings(BaseSettings):
    """
    Настройки приложения для генерации данных.
    """

    model_config = SettingsConfigDict(case_sensitive=False, env_file=str(CONFIG_DIR / "env.example"), extra="ignore")

    bootstrap_servers: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    topic_name: str = Field(..., alias="KAFKA_TOPIC_NAME")
    topic_name_raw: str = Field(..., alias="KAFKA_TOPIC_NAME_RAW")
    poll_timeout: float = Field(default=DEFAULT_POLL_TIMEOUT_SECONDS, alias="KAFKA_PRODUCER_POLL_TIMEOUT_SECONDS")
    acks: str = Field(default=DEFAULT_PRODUCER_ACKS, alias="KAFKA_PRODUCER_ACKS")
    retries: int = Field(default=DEFAULT_PRODUCER_RETRIES, alias="KAFKA_PRODUCER_RETRIES")

    sasl_mechanism: str = Field("PLAIN", alias="KAFKA_SASL_MECHANISM")
    security_protocol: str = Field(..., alias="KAFKA_SECURITY_PROTOCOL")
    sasl_username: str = Field(..., alias="KAFKA_SASL_USERNAME")
    sasl_password: str = Field(..., alias="KAFKA_SASL_PASSWORD")
    ssl_ca_location: str = Field(..., alias="KAFKA_SSL_CA_LOCATION")

    @property
    def broker_config(self) -> dict:
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "log_level": DEFAULT_LOG_LEVEL,
            "acks": self.acks,
            "retries": self.retries,
            "security.protocol": self.security_protocol,
            "sasl.mechanism": self.sasl_mechanism,
            "sasl.username": self.sasl_username,
            "sasl.password": self.sasl_password,
            "ssl.ca.location": self.ssl_ca_location,
        }


def get_producer_settings() -> ProducerSettings:
    return ProducerSettings()
