from pydantic import BaseModel, Field


class PremiumBrandsSchema(BaseModel):
    brand: str = Field(..., description="Название бренда", validation_alias="BRAND")
    avg_price: float = Field(..., description="Средняя цена товаров бренда", validation_alias="AVG_PRICE")
    product_count: int = Field(..., description="Количество товаров бренда", validation_alias="PRODUCT_COUNT")


class LowStockSchema(BaseModel):
    product_id: str = Field(..., description="ID товара", validation_alias="PRODUCT_ID")
    name: str = Field(..., description="Название товара", validation_alias="NAME")
    category: str = Field(..., description="Категория товара", validation_alias="CATEGORY")
    available_stock: int = Field(..., description="Доступный остаток", validation_alias="AVAILABLE_STOCK")
    price: float = Field(..., description="Цена товара", validation_alias="PRICE")


class CategoryStatsSchema(BaseModel):
    category: str = Field(..., description="Категория товара", validation_alias="CATEGORY")
    product_count: int = Field(..., description="Количество товаров в категории", validation_alias="PRODUCT_COUNT")
    avg_price: float = Field(..., description="Средняя цена товаров в категории", validation_alias="AVG_PRICE")
    total_available_stock: int = Field(
        ..., description="Общий доступный остаток в категории", validation_alias="TOTAL_AVAILABLE_STOCK"
    )


class RecommendationSchema(BaseModel):
    item_id: str = Field(..., description="ID рекомендованного товара", validation_alias="ITEM_ID")
    recommendation_type: str = Field(..., description="Тип рекомендации", validation_alias="RECOMMENDATION_TYPE")
    score: float = Field(..., description="Оценка релевантности рекомендации", validation_alias="SCORE")
    product_count: int | None = Field(
        None, description="Количество товаров в рекомендации (для категорий)", validation_alias="PRODUCT_COUNT"
    )
    avg_price: float | None = Field(
        None, description="Средняя цена товаров в рекомендации (для категорий)", validation_alias="AVG_PRICE"
    )
    generated_at: str = Field(..., description="Время генерации рекомендации", validation_alias="GENERATED_AT")
