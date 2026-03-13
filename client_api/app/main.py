import logging
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.db import elastic
from src.routers import products, recommendations
from src.services.logs import get_kafka_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    elastic.es = AsyncElasticsearch(hosts=[settings.api_elasticsearch_url])
    logger.info("Starting Client API...")
    yield
    logger.info("Shutting down Client API...")
    get_kafka_service().flush()
    await elastic.es.close()


app = FastAPI(
    title=settings.app_name,
    description="API для поиска товаров и получения рекомендаций",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(products.router)
app.include_router(recommendations.router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
