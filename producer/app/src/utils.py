import datetime as dt
import random

from faker import Faker

from src.const import BRANDS, CATEGORIES, CATEGORY_NAMES, FORBIDDEN_CATEGORIES, PRODUCT_NAMES, STORE_UUIDS


def generate_mock_data(data_generator: Faker) -> dict:
    """Генерация данных от магазинов."""

    def get_product_name() -> str:
        if random.random() < 0.1:  # NOTE: в 10% случаев используется значение из PRODUCT_NAMES
            return random.choice(PRODUCT_NAMES)
        return data_generator.catch_phrase()

    category_name = random.choice(CATEGORY_NAMES)
    new_message = {
        "product_id": data_generator.uuid4(),
        "name": get_product_name(),
        "description": data_generator.text(max_nb_chars=200),
        "price": {"amount": round(random.uniform(1000, 10000), 2), "currency": "RUB"},
        "category": category_name,
        "brand": random.choice(BRANDS),
        "stock": {"available": random.randint(0, 500), "reserved": random.randint(0, 100)},
        "sku": data_generator.unique.bothify(text="??###"),
        "tags": random.sample(CATEGORIES[category_name], k=random.randint(1, 3)),
        "images": [
            {"url": data_generator.image_url(), "alt": data_generator.sentence()} for _ in range(random.randint(1, 3))
        ],
        "specifications": {
            "weight": f"{random.randint(30, 100)}g",
            "dimensions": f"{random.randint(30, 50)}mm x {random.randint(30, 50)}mm x {random.randint(5, 15)}mm",
        },
        "created_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "updated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "index": "products",
        "store_id": random.choice(STORE_UUIDS),
    }
    if new_message["category"] in FORBIDDEN_CATEGORIES:
        new_message["brand"] = data_generator.company()
    if tags := new_message.get("tags"):
        if any(tag in FORBIDDEN_CATEGORIES for tag in tags):
            new_message["brand"] = data_generator.company()
    return new_message


def format_price(amount, currency):
    return f"{amount:.2f} {currency}"
