"""The Conftest module.

This module contains pytest fixtures.
"""

from pathlib import Path

import pytest

from grayven.grand_comics_database import GrandComicsDatabase
from grayven.sqlite_cache import SQLiteCache


@pytest.fixture(scope="session")
def session() -> GrandComicsDatabase:
    """Set the GrandComicsDatabase session fixture."""
    return GrandComicsDatabase(
        cache=SQLiteCache(path=Path("tests/cache.sqlite"), expiry=None), timeout=5
    )
