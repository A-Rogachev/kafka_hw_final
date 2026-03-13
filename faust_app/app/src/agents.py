from typing import Final

import faust

from src.core.types import ProductMessage
from src.dependencies import AppDependencies

INTERVAL_TO_GET_BANNED_WORDS_SEC: Final[int] = 3
AMOUNT_OF_BANNED_WORDS_TO_GET: Final[int] = 100


def app_agents(app: faust.App, dependencies: AppDependencies) -> None:
    """Регистрация агентов в приложении."""

    @app.agent(channel=dependencies.topics.shops_stock_received)
    async def process_shops_stock_received(messages: faust.Stream[bytes]) -> None:
        """Агент для обработки данных о товарах, полученных от магазинов."""
        async for msg in messages:
            try:
                msg: ProductMessage = ProductMessage.loads(msg)
            except Exception as e:
                dependencies.logger.error("Error processing shop stock data: %s", str(e))
            else:
                record: dict[str, set[str]] = dependencies.tables.banned_products["global"]
                if msg.category in record["categories"]:
                    await dependencies.topics.shops_stock_banned.send(key=msg.product_id, value=msg)
                    dependencies.logger.warning("Product %s banned due to category %s.", msg.product_id, msg.category)
                elif record["tags"].intersection(msg.tags):
                    await dependencies.topics.shops_stock_banned.send(key=msg.product_id, value=msg)
                    dependencies.logger.warning("Product %s banned due to tags %s.", msg.product_id, msg.tags)
                elif msg.name in record["product_names"]:
                    await dependencies.topics.shops_stock_banned.send(key=msg.product_id, value=msg)
                    dependencies.logger.warning("Product %s banned due to name %s", msg.product_id, msg.name)
                else:
                    await dependencies.topics.shops_stock_accepted.send(key=msg.product_id, value=msg)
                    dependencies.logger.info("Product %s accepted", msg.product_id)
