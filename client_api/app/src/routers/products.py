import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.dependencies import kafka_service_dep, product_service
from src.models import ProductModel, UserActionModel
from src.services.logs import KafkaService
from src.services.products import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/search", response_model=list[ProductModel])
async def search_products(
    query: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество результатов"),
    user_id: str = Query("anonymous", description="ID пользователя"),
    service: ProductService = Depends(product_service),
    kafka: KafkaService = Depends(kafka_service_dep),
):
    """
    Поиск товаров по названию, описанию, категории, бренду или тегам.

    Логирует действие пользователя в Kafka для аналитики.
    """
    kafka.log_user_action(
        UserActionModel(
            user_id=user_id,
            action_type="search",
            query=query,
            timestamp=dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        )
    )
    if not (results := await service.search_products(query=query, limit=limit)):
        return []
    return results


@router.get("/{product_id}", response_model=ProductModel)
async def get_product(
    product_id: str,
    user_id: str = Query("anonymous", description="ID пользователя"),
    service: ProductService = Depends(product_service),
    kafka: KafkaService = Depends(kafka_service_dep),
):
    """Получение товара по ID"""
    kafka.log_user_action(
        UserActionModel(
            user_id=user_id,
            action_type="view",
            product_id=product_id,
            timestamp=dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        )
    )
    if not (product := await service.get_product_by_id(product_id)):
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/category/{category}", response_model=list[ProductModel])
async def get_products_by_category(
    category: str,
    limit: int = Query(10, ge=1, le=100),
    service: ProductService = Depends(product_service),
):
    """Получение товаров по категории"""
    return await service.search_by_category(category=category, limit=limit)
