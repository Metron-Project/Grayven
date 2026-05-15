import pytest
from responses import RequestsMock as Mocker

from grayven.errors import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_not_found(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/invalid/"
        mock.get(url=url, status=404, json={"detail": "Not found."})
        with pytest.raises(ServiceError):
            mock_session._get_request(endpoint="/invalid")  # noqa: SLF001
        mock.assert_call_count(url, 1)


def test_timeout(session: GrandComicsDatabase) -> None:
    session._timeout = 0.00001  # noqa: SLF001
    with pytest.raises(ServiceError):
        session.get_publisher(publisher_id=1)
