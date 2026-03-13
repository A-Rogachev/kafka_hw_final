from http import HTTPStatus

import faust
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from src.dependencies import AppDependencies


def banned_products_view(app: faust.App, dependencies: AppDependencies) -> None:
    """Регистрация представления для управления списком запрещенных товаров."""

    @app.page("/banned_products/")
    async def get(self, request: Request) -> Response:
        """Получение списка запрещенных товаров (категории, )."""
        products: set[str] = dependencies.tables.banned_products.get("global", set())
        return self.json(products, status=HTTPStatus.OK)
