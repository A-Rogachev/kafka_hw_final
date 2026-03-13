import logging

from confluent_kafka import Producer

from src.core.config import settings
from src.models import UserActionModel

logger = logging.getLogger(__name__)


class KafkaService:
    def __init__(self):
        config = {
            "bootstrap.servers": settings.api_kafka_bootstrap_servers,
            "client.id": "client-api-producer",
            "acks": "all",
            "retries": 3,
            "linger.ms": 100,
        }

        # Добавляем настройки безопасности, если они указаны
        if settings.kafka_security_protocol != "PLAINTEXT":
            config["security.protocol"] = settings.kafka_security_protocol

            if settings.kafka_sasl_mechanism:
                config["sasl.mechanism"] = settings.kafka_sasl_mechanism
                config["sasl.username"] = settings.kafka_sasl_username
                config["sasl.password"] = settings.kafka_sasl_password

            if settings.kafka_ssl_ca_location:
                config["ssl.ca.location"] = settings.kafka_ssl_ca_location
                config["ssl.endpoint.identification.algorithm"] = "none"

        self.producer = Producer(config)

    def log_user_action(self, action: UserActionModel):
        """Логирование действий пользователя в Kafka для аналитики"""
        try:
            message = action.model_dump_json()
            self.producer.produce(
                topic=settings.api_kafka_user_actions_topic_name,
                key=action.user_id.encode("utf-8") if action.user_id else None,
                value=message.encode("utf-8"),
                callback=self._delivery_report,
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error("Kafka produce error: %s", e)

    def _delivery_report(self, err, msg):
        if err:
            logger.error("Message delivery failed: %s", err)
        else:
            logger.debug("Message delivered to %s [%s]", msg.topic(), msg.partition())

    def flush(self):
        """Ожидание отправки всех сообщений"""
        self.producer.flush()
        self.producer.close()


kafka_service = KafkaService()


def get_kafka_service() -> KafkaService:
    """Возвращает экземпляр сервиса для логирования в Kafka"""
    return kafka_service
