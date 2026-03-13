import logging
from typing import Any, cast

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as es_exceptions

from src.core.config import settings

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def search_products(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Поиск товаров по имени/описанию"""
        try:
            async with await self.client() as es:
                response = await cast(AsyncElasticsearch, es).search(
                    index=settings.api_elasticsearch_index,
                    body={
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^3", "description", "category^2", "brand^2", "tags"],
                                "fuzziness": "AUTO",
                            }
                        },
                        "size": limit,
                    },
                )
            hits = response["hits"]["hits"]
            return [{**hit["_source"], "_score": hit["_score"]} for hit in hits]
        except es_exceptions.NotFoundError:
            logger.warning("Index %s not found", settings.api_elasticsearch_index)
            return []
        except Exception as e:
            logger.error("Search error: %s", e)
            return []

    async def get_product_by_id(self, product_id: str) -> dict[str, Any] | None:
        """Получение товара по ID"""
        try:
            async with await self.client() as es:
                response = await cast(AsyncElasticsearch, es).search(
                    index=settings.api_elasticsearch_index, body={"query": {"term": {"product_id": product_id}}}
                )
                hits = response["hits"]["hits"]
                if hits:
                    return hits[0]["_source"]
                return None
        except Exception as e:
            logger.error("Get product error: %s", e)
            return None

    async def search_by_category(self, category: str, limit: int = 10) -> list[dict[str, Any]]:
        """Поиск товаров по категории"""
        try:
            async with await self.client() as es:
                response: ObjectApiResponse = await cast(AsyncElasticsearch, es).search(
                    index=settings.api_elasticsearch_index,
                    body={"query": {"term": {"category": category}}, "size": limit, "sort": [{"price.amount": "asc"}]},
                )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error("Category search error: %s", e)
            return []
