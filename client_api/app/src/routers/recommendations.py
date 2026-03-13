import datetime as dt

from fastapi import APIRouter, Depends, Query

from src.core.dependencies import kafka_service_dep, recommendation_service
from src.models import UserActionModel
from src.schemas import CategoryStatsSchema, LowStockSchema, PremiumBrandsSchema, RecommendationSchema
from src.services.logs import KafkaService
from src.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=list[RecommendationSchema])
async def get_recommendations(
    recommendation_type: str = Query("category", description="Тип рекомендаций: category, brand"),
    limit: int = Query(10, ge=1, le=100),
    user_id: str = Query("anonymous", description="ID пользователя"),
    service: RecommendationService = Depends(recommendation_service),
    kafka: KafkaService = Depends(kafka_service_dep),
):
    """
    Получение рекомендаций из ksqlDB.

    Типы рекомендаций:
    - category: рекомендации по категориям
    - brand: рекомендации по брендам
    """
    kafka.log_user_action(
        UserActionModel(
            user_id=user_id,
            action_type="recommendation_request",
            query=recommendation_type,
            timestamp=dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        )
    )
    return await service.get_recommendations_by_type(recommendation_type=recommendation_type, limit=limit)


@router.get("/category-stats")
async def get_category_stats(
    service: RecommendationService = Depends(recommendation_service),
) -> list[CategoryStatsSchema]:
    """Получение статистики по категориям из ksqlDB"""
    return await service.get_category_stats()


@router.get("/low-stock")
async def get_low_stock_products(
    service: RecommendationService = Depends(recommendation_service),
) -> list[LowStockSchema]:
    """Получение товаров с низким остатком из ksqlDB"""
    return await service.get_low_stock_products()


@router.get("/premium-brands")
async def get_premium_brands(
    service: RecommendationService = Depends(recommendation_service),
) -> list[PremiumBrandsSchema]:
    """Получение премиум брендов из ksqlDB"""
    return await service.get_premium_brands()
