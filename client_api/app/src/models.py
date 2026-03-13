from pydantic import BaseModel


class PriceModel(BaseModel):
    amount: float
    currency: str


class StockModel(BaseModel):
    available: int
    reserved: int


class ProductModel(BaseModel):
    product_id: str
    name: str
    description: str | None = None
    price: PriceModel
    category: str
    brand: str
    stock: StockModel
    sku: str
    tags: list[str] = []
    store_id: str


class UserActionModel(BaseModel):
    user_id: str | None = "anonymous"
    action_type: str  # NOTE: возможные варианты -> "search", "view", "recommendation_request"
    query: str | None = None
    product_id: str | None = None
    timestamp: str
