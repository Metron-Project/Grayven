"""The SQLiteCache module.

This module provides the following classes:
- SQLiteCache
"""

__all__ = ["SQLiteCache"]
import json
import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from grayven import get_cache_root
from grayven.cache.schemas import CacheData

LOGGER = logging.getLogger(__name__)


class SQLiteCache:
    """The SQLiteCache object to cache responses from GrandComicsDatabase.

    Args:
        path: Path to database.
        expiry: How long to keep cache results.
    """

    def __init__(self, path: Path | None = None, expiry: timedelta | None = timedelta(days=14)):
        self._db_path = path or (get_cache_root() / "cache.sqlite")
        self._expiry = expiry
        self.create_table()
        self.cleanup()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection]:
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            if conn:
                conn.close()

    def create_table(self) -> None:
        """Create the cache table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS queries (
            query TEXT NOT NULL PRIMARY KEY,
            response TEXT NOT NULL,
            `timestamp` DATETIME NOT NULL
        );
        """
        with self._connect() as conn:
            conn.execute(query)
            conn.commit()

    def select(self, key: str) -> CacheData | None:
        """Retrieve a cached entry by URL.

        Args:
            key: The URL used as the cache key.

        Returns:
            A `CacheData` instance if a matching record exists, otherwise `None`.
        """
        if self._expiry:
            query = """
            SELECT query, response, `timestamp`
            FROM queries
            WHERE query = ? AND `timestamp` > ?;
            """
            expiry: datetime = datetime.now(tz=timezone.utc) - self._expiry  # ty: ignore[invalid-assignment]
            args = (query, expiry.isoformat())
        else:
            query = """
            SELECT query, response, `timestamp`
            FROM queries
            WHERE query = ?;
            """
            args = (query,)
        with self._connect() as conn:
            if row := conn.execute(query, args).fetchone():
                try:
                    return CacheData(
                        query=row["query"],
                        response=json.loads(row["response"]),
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                    )
                except json.JSONDecodeError as err:
                    LOGGER.warning(err)
                    self.delete(key=key)
            return None

    def insert(self, key: str, response: dict[str, Any], timestamp: datetime | None = None) -> None:
        """Insert data into the cache database.

        Args:
            key: The URL that was requested, used as the cache key.
            response: The response body returned by the server.
            timestamp: The UTC datetime at which the response was fetched and stored.
                Defaults to the current UTC datetime.
        """
        query = """
        INSERT INTO queries (query, response, `timestamp`)
        VALUES (?, ?, ?);
        """
        with self._connect() as conn:
            conn.execute(
                query,
                (
                    key,
                    json.dumps(response),
                    (timestamp or datetime.now(tz=timezone.utc)).isoformat(),
                ),
            )
            conn.commit()

    def delete(self, key: str) -> None:
        """Delete a cached entry by URL.

        Args:
            key: The URL of the entry to remove.
        """
        query = """
        DELETE FROM queries
        WHERE query = ?;
        """
        with self._connect() as conn:
            conn.execute(query, (key,))
            conn.commit()

    def cleanup(self) -> None:
        """Remove all expired entries from the cache database."""
        if not self._expiry:
            return
        query = """
        DELETE FROM queries
        WHERE timestamp < ?;
        """
        expiry: datetime = datetime.now(tz=timezone.utc) - self._expiry  # ty: ignore[invalid-assignment]
        with self._connect() as conn:
            conn.execute(query, (expiry.isoformat(),))
            conn.commit()
