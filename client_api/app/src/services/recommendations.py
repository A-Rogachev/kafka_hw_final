import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = httpx.Timeout(30.0)

    async def execute_query(self, ksql: str) -> dict[str, Any]:
        """Выполнение ksqlDB запроса."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    json={"ksql": ksql, "streamsProperties": {}},
                    headers={"Accept": "application/vnd.ksql.v1+json"},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("ksqlDB query error: %s", e)
            return {"error": str(e)}
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            return {"error": str(e)}

    async def get_recommendations_by_type(self, recommendation_type: str, limit: int = 10) -> list[dict[str, Any]]:
        """Получение рекомендаций по типу из материализованной таблицы"""
        ksql = """
        SELECT item_id, recommendation_type, score, product_count, avg_price, generated_at
        FROM latest_recommendations;
        """
        result: list[dict[str, Any]] = await self.execute_query(ksql)
        all_recommendations: list[dict[str, Any]] = self._parse_ksqldb_response(result)
        return [rec for rec in all_recommendations if rec.get("RECOMMENDATION_TYPE") == "top_" + recommendation_type][
            :limit
        ]

    async def get_category_stats(self) -> list[dict[str, Any]]:
        """Получение статистики по категориям"""
        ksql = """
        SELECT category, product_count, avg_price, total_available_stock
        FROM category_stats;
        """
        result: list[dict[str, Any]] = await self.execute_query(ksql)
        return self._parse_ksqldb_response(result)

    async def get_low_stock_products(self) -> list[dict[str, Any]]:
        """Получение товаров с низким остатком"""
        ksql = """
        SELECT product_id, name, category, available_stock, price
        FROM low_stock_products;
        """
        result: list[dict[str, Any]] = await self.execute_query(ksql)
        return self._parse_ksqldb_response(result)

    async def get_premium_brands(self) -> list[dict[str, Any]]:
        """Получение премиум брендов"""
        ksql = """
        SELECT brand, avg_price, product_count
        FROM premium_brands;
        """
        result: list[dict[str, Any]] = await self.execute_query(ksql)
        return self._parse_ksqldb_response(result)

    def _parse_ksqldb_response(self, response: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Парсинг ответа ksqlDB"""
        if isinstance(response, dict) and "error" in response:
            logger.error("ksqlDB error: %s", response["error"])
            return []
        try:
            if not isinstance(response, list) or not response:
                return []
            header_obj = next((item for item in response if "header" in item), None)
            if not header_obj:
                logger.error("No header found in response")
                return []
            schema = header_obj["header"].get("schema", "")
            column_names = []
            for part in schema.split(","):
                match = re.search(r"`([^`]+)`", part.strip())
                if match:
                    column_names.append(match.group(1))
                else:
                    words = part.strip().split()
                    if words:
                        column_names.append(words[0])
            if not column_names:
                logger.error("Could not parse column names from schema")
                return []
            results = []
            for item in response:
                if "row" in item and "columns" in item["row"]:
                    columns = item["row"]["columns"]
                    row_dict = dict(zip(column_names, columns))
                    results.append(row_dict)
            return results
        except Exception as e:
            logger.error("Parse error: %s", e)
            return []
