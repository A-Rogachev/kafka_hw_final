import faust

from src.core.const import Defaults
from src.core.types import AppTables

DEFAULT_PARTITIONS_AMOUNT: int = 3


def create_tables(faust_app: faust.App) -> AppTables:
    """
    Функция для создания таблиц приложения.

    :param faust_app: faust.App, экземпляр Faust приложения

    :return: AppTables, таблицы приложения
    """
    return AppTables(
        banned_products=faust_app.Table(
            name="banned_products",
            default=lambda: Defaults.to_dict(),
            help="Запрещенные товары",
            partitions=DEFAULT_PARTITIONS_AMOUNT,
        ),
    )
