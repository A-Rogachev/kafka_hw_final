from typing import Final


class Defaults:
    BANNED_CATEGORIES: Final[set[str]] = {
        "weapons",
        "drugs",
        "counterfeit",
        "stolen",
    }
    BANNED_TAGS: Final[set[str]] = {
        "prohibited",
        "forbidden",
        "restricted",
        "dangerous",
        "illegal",
        "controlled",
        "fake",
        "unauthorized",
        "imitation",
        "fraudulent",
        "recovered",
        "missing",
        "reported",
    }
    BANNED_PRODUCTS: Final[set[str]] = {
        "gun",
        "pistol",
        "rifle",
        "fake_watch",
        "stolen_phone",
        "illegal_drugs",
        "1984 the book",
    }

    @classmethod
    def to_dict(cls) -> dict[str, set[str]]:
        return {
            "categories": cls.BANNED_CATEGORIES,
            "tags": cls.BANNED_TAGS,
            "product_names": cls.BANNED_PRODUCTS,
        }
