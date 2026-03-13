import json
import logging
import random
from time import sleep

from confluent_kafka import KafkaException, Message, Producer
from faker import Faker

from src.config import ProducerSettings, get_producer_settings
from src.utils import generate_mock_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_kafka_producer(settings: ProducerSettings) -> Producer:
    while True:
        try:
            producer = Producer(settings.broker_config)
            producer.list_topics(timeout=3)
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            sleep(random.uniform(1, 3))
            continue
        else:
            logger.info("Kafka producer created successfully.")
            break
    return producer


def main() -> None:
    """Основная функция приложения."""

    def delivery_report(err: KafkaException | None, msg: Message) -> None:
        if err:
            logger.error(f"Failed: {err}")
            return
        logger.info(f"Message sent: partition={msg.partition()}, offset={msg.offset()}")

    settings: ProducerSettings = get_producer_settings()
    producer: Producer = create_kafka_producer(settings)
    faker = Faker()
    try:
        while True:
            try:
                mock_data: dict = generate_mock_data(faker)
                producer.produce(
                    topic=settings.topic_name_raw,
                    key=bytes(mock_data["product_id"], "utf-8"),
                    value=json.dumps(mock_data),
                    on_delivery=delivery_report,
                )
                producer.poll(0)
            except KafkaException as e:
                logger.error(f"Failed to produce message: {e}")
            sleep(random.uniform(0, 1))
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        producer.flush()
        producer.close()
        logger.info("Producer closed.")


if __name__ == "__main__":
    main()
