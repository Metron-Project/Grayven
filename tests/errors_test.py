import pytest
from requests.exceptions import Timeout
from responses import RequestsMock as Mocker

from grayven.errors import AuthenticationError, RateLimitError, ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_not_found(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/invalid/"
        mock.get(url=url, status=404, json={"detail": "Not found."})
        with pytest.raises(ServiceError):
            mock_session._get_request(endpoint="/invalid")  # noqa: SLF001
        mock.assert_call_count(url, 1)


def test_timeout(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/publisher/1/"
        mock.get(url=url, body=Timeout())
        with pytest.raises(ServiceError):
            mock_session.get_publisher(publisher_id=1)
        mock.assert_call_count(url, 1)


def test_ratelimit(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/publisher/1/"
        mock.get(url=url, status=429, json={}, headers={"Retry-After": "60"})
        with pytest.raises(RateLimitError):
            mock_session.get_publisher(publisher_id=1)
        mock.assert_call_count(url, 1)


def test_authentication(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/publisher/1/"
        mock.get(url=url, status=401, json={"detail": "Invalid username/password."})
        with pytest.raises(AuthenticationError):
            mock_session.get_publisher(publisher_id=1)
        mock.assert_call_count(url, 1)
