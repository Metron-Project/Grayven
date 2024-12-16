"""The Publisher test module.

This module contains tests for Publisher objects.
"""

from datetime import datetime

import pytest

from grayven.exceptions import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_publisher(session: GrandComicsDatabase) -> None:
    """Test using the publisher endpoint with a valid id."""
    result = session.get_publisher(id=54)
    assert result is not None
    assert result.id == 54

    assert str(result.api_url) == "https://www.comics.org/api/publisher/54/?format=json"
    assert result.country == "us"
    assert result.modified == datetime(2024, 12, 16, 17, 1, 37)  # noqa: DTZ001
    assert result.name == "DC"
    assert result.year_began == 1935
    assert result.year_ended is None
    assert result.year_began_uncertain is False
    assert result.year_ended_uncertain is False
    assert result.year_overall_began is None
    assert result.year_overall_ended is None
    assert result.year_overall_began_uncertain is False
    assert result.year_overall_ended_uncertain is False
    assert str(result.url) == "http://www.dccomics.com/"
    assert result.brand_count == 28
    assert result.indicia_publisher_count == 53
    assert result.series_count == 9628
    assert result.issue_count == 56104


def test_publisher_fail(session: GrandComicsDatabase) -> None:
    """Test using the publisher endpoint with an invalid id."""
    with pytest.raises(ServiceError):
        session.get_publisher(id=-1)


def test_list_publishers(session: GrandComicsDatabase) -> None:
    """Test using the list_publishers endpoint with a valid search."""
    results = session.list_publishers()
    assert len(results) >= 500
