from functools import lru_cache

from src.core.config import settings
from src.db.elastic import get_elastic
from src.services.logs import KafkaService, get_kafka_service
from src.services.products import ProductService
from src.services.recommendations import RecommendationService


@lru_cache
def product_service() -> ProductService:
    """Экземпляр сервиса для работы с товарами"""
    return ProductService(client=get_elastic)


@lru_cache
def recommendation_service() -> RecommendationService:
    """Экземпляр сервиса для получения рекомендаций из ksqlDB"""
    return RecommendationService(base_url=settings.api_ksqldb_url)


def kafka_service_dep() -> KafkaService:
    """Экземпляр сервиса для логирования действий пользователя в Kafka"""
    return get_kafka_service()
