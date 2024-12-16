"""The Exceptions test module.

This module contains tests for Exceptions.
"""

import pytest

from grayven.exceptions import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_not_found(session: GrandComicsDatabase) -> None:
    """Test a 404 Not Found raises a ServiceError."""
    with pytest.raises(ServiceError):
        session._get_request(endpoint="/invalid")  # noqa: SLF001


def test_timeout() -> None:
    """Test a TimeoutError for slow responses."""
    session = GrandComicsDatabase(timeout=1, cache=None)
    with pytest.raises(ServiceError):
        session.get_publisher(id=1)
