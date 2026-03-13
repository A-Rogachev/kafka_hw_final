from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[4]


class AppSettings(BaseSettings):
    """Настройки приложения для потоковой обработки данных."""

    model_config = SettingsConfigDict(case_sensitive=False, env_file=str(CONFIG_DIR / "env.example"), extra="ignore")

    data_store: str = Field("memory://", alias="FAUST_DATA_STORE")
    broker_address: str = Field(..., alias="KAFKA_BOOTSTRAP_SERVERS")

    sasl_mechanism: str = Field("PLAIN", alias="KAFKA_SASL_MECHANISM")
    security_protocol: str = Field(..., alias="KAFKA_SECURITY_PROTOCOL")
    sasl_username: str = Field(..., alias="KAFKA_SASL_USERNAME")
    sasl_password: str = Field(..., alias="KAFKA_SASL_PASSWORD")
    ssl_ca_location: str = Field(..., alias="KAFKA_SSL_CA_LOCATION")

    @property
    def broker_credentials(self):
        """Faust SSL/SASL configuration."""
        import ssl

        import faust

        ssl_context = ssl.create_default_context(cafile=self.ssl_ca_location)
        ssl_context.check_hostname = False

        return faust.auth.SASLCredentials(
            username=self.sasl_username,
            password=self.sasl_password,
            mechanism=self.sasl_mechanism,
            ssl_context=ssl_context,
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
