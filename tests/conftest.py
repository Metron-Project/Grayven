import os
from pathlib import Path

import pytest

from grayven.cache import SQLiteCache
from grayven.grand_comics_database import GrandComicsDatabase


@pytest.fixture(scope="session")
def gcd_email() -> str:
    return os.getenv("GCD_EMAIL", "<EMAIL>")


@pytest.fixture(scope="session")
def gcd_password() -> str:
    return os.getenv("GCD_PASSWORD", "passwrd")


@pytest.fixture(scope="session")
def session(gcd_email: str, gcd_password: str) -> GrandComicsDatabase:
    return GrandComicsDatabase(
        email=gcd_email,
        password=gcd_password,
        cache=SQLiteCache(path=Path("tests/cache.sqlite"), expiry=None),
    )
