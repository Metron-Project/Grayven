import pytest

from grayven.errors import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_not_found(session: GrandComicsDatabase) -> None:
    with pytest.raises(ServiceError):
        session._perform_get_request(endpoint="/invalid")  # noqa: SLF001


def test_timeout(gcd_email: str, gcd_password: str) -> None:
    session = GrandComicsDatabase(gcd_email, gcd_password, timeout=1, cache=None)
    with pytest.raises(ServiceError):
        session.get_publisher(publisher_id=1)
