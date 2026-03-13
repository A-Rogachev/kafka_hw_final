from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch | None:
    """
    Возвращает адаптер Elasticsearch для взаимодействия с данными из хранилища.

    :return: AsyncElasticsearch | None, адаптер Elasticsearch
    """
    return es
