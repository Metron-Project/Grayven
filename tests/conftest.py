"""The Conftest module.

This module contains pytest fixtures.
"""

import os
from pathlib import Path

import pytest

from grayven.grand_comics_database import GrandComicsDatabase
from grayven.sqlite_cache import SQLiteCache


@pytest.fixture(scope="session")
def gcd_email() -> str:
    """Email address for testing."""
    return os.getenv("GCD_EMAIL")


@pytest.fixture(scope="session")
def gcd_password() -> str:
    """Password for testing."""
    return os.getenv("GCD_PASSWORD")


@pytest.fixture(scope="session")
def session(gcd_email: str, gcd_password: str) -> GrandComicsDatabase:
    """Set the GrandComicsDatabase session fixture."""
    return GrandComicsDatabase(
        email=gcd_email,
        password=gcd_password,
        cache=SQLiteCache(path=Path("tests/cache.sqlite"), expiry=None),
        timeout=5,
    )
