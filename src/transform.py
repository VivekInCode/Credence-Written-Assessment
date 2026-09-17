"""Route provider JSON. Each provider keeps its existing output contract."""

from src.china import transform_china
from src.india import transform_india
from src.singapore import transform_singapore


def transform(provider: str, payload):
    name = (provider or "").strip().lower()
    if name == "india":
        return transform_india(payload)
    if name == "china":
        return transform_china(payload)
    if name == "singapore":
        return transform_singapore(payload)
    return {}
