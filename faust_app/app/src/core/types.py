from dataclasses import dataclass
from typing import Literal

import faust


class ProductMessage(faust.Record, serializer="json"):
    """Сообщение о товаре от магазина."""

    product_id: str
    name: str
    description: str
    price: dict[str, float | str]
    category: str
    brand: str
    stock: dict[Literal["available", "reserved"], int]
    sku: str
    tags: list[str]
    images: list[dict[Literal["url", "alt"], str]]
    specifications: dict[Literal["weight", "dimensions"], str]
    created_at: str
    updated_at: str
    index: str
    store_id: str


class BannedProduct(faust.Record, serializer="json"):
    name: str
    type: Literal["category", "tag", "name"]


@dataclass
class AppTables:
    """Таблицы приложения."""

    banned_products: faust.Table[dict[str, set[str]]]


@dataclass(slots=True)
class AppTopics:
    """Топики приложения."""

    shops_stock_accepted: faust.Topic
    shops_stock_received: faust.Topic
    shops_stock_banned: faust.Topic
