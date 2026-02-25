__all__ = ["CacheData"]

from datetime import datetime
from typing import Any

from grayven.schemas._base import BaseModel


class CacheData(BaseModel):
    """A single entry stored in the cache.

    Attributes:
        query: The URL that was requested, used as the cache key.
        response: The response body returned by the server.
        timestamp: The UTC datetime at which the response was fetched and stored.
    """

    query: str
    response: dict[str, Any]
    timestamp: datetime
