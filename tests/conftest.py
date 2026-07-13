import os
from datetime import timedelta
from pathlib import Path

import pytest
from requests_cache import NEVER_EXPIRE

from grayven.grand_comics_database import GrandComicsDatabase


@pytest.fixture(scope="session")
def email() -> str:
    return os.getenv("GCD_EMAIL", "UNSET")


@pytest.fixture(scope="session")
def password() -> str:
    return os.getenv("GCD_PASSWORD", "UNSET")


@pytest.fixture
def session(email: str, password: str, tmp_path: Path) -> GrandComicsDatabase:
    return GrandComicsDatabase(
        email=email,
        password=password,
        cache_path=Path("tests") / "cache.sqlite",
        cache_expiry=NEVER_EXPIRE,
        ratelimit_path=tmp_path / "grayven-ratelimit.sqlite",
    )


@pytest.fixture
def mock_session(tmp_path: Path) -> GrandComicsDatabase:
    return GrandComicsDatabase(
        email="UNSET",
        password="UNSET",  # noqa: S106
        base_url="https://comics.mock/api",
        cache_path=tmp_path / "grayven.sqlite",
        cache_expiry=timedelta(seconds=1),
        ratelimit_path=tmp_path / "grayven-ratelimit.sqlite",
    )
