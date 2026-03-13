from collections.abc import Sequence
from typing import Callable, TypeAlias

import faust

from src.agents import app_agents
from src.core.config import AppSettings, get_settings
from src.core.logger import setup_logger
from src.dependencies import DEPENDENCIES, AppDependencies
from src.tables import create_tables
from src.topics import register_topics
from src.views import banned_products_view

RegisterMethod: TypeAlias = Sequence[Callable[[faust.App, AppDependencies], None]]


def register_views(
    app_object: faust.App,
    app_dependenies: AppDependencies,
    views_decorators: RegisterMethod,
) -> None:
    """
    Регистрация представления в приложении.

    :param app_object: faust.App, экземпляр приложения
    :param app_dependencies: AppDependencies, зависимости для функционирования приложения
    :views_decorators: views_decorators: RegisterMethod, список функций регистрации
        представлений для приложения

    :return: None
    """
    for register_view in views_decorators:
        register_view(app_object, app_dependenies)


register_agents = register_views

settings: AppSettings = get_settings()
app = faust.App(
    id="faust_app",
    broker=settings.broker_address,
    store=settings.data_store,
    broker_credentials=settings.broker_credentials,
    value_serializer="raw",
)

DEPENDENCIES.tables = create_tables(app)
DEPENDENCIES.topics = register_topics(app)
DEPENDENCIES.logger = setup_logger(name="faust_logger")

register_views(app, DEPENDENCIES, [banned_products_view])
register_agents(app, DEPENDENCIES, [app_agents])


if __name__ == "__main__":
    app.main()
