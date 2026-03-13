import faust

from src.core.types import AppTopics


def register_topics(faust_app: faust.App) -> AppTopics:
    """
    Регистрация топиков кафки для приложения.

    :param faust_app: faust.App, экземпляр Faust приложения

    :return: AppTopics, топики кафки
    """
    return AppTopics(
        shops_stock_received=faust_app.topic(
            "shops_stock_received",
            key_type=str,
            value_type=bytes,
            partitions=2,
        ),
        shops_stock_accepted=faust_app.topic(
            "shops_stock_accepted",
            key_type=str,
            value_type=bytes,
            partitions=2,
        ),
        shops_stock_banned=faust_app.topic(
            "shops_stock_banned",
            key_type=str,
            value_type=bytes,
            partitions=2,
        ),
    )
