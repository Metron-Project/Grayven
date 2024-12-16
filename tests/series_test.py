"""The Series test module.

This module contains tests for Series objects.
"""

import pytest

from grayven.exceptions import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_series(session: GrandComicsDatabase) -> None:
    """Test using the series endpoint with a valid id."""
    result = session.get_series(id=13519)
    assert result is not None
    assert result.id == 13519

    assert result.api_url == "https://www.comics.org/api/series/13519/?format=json"
    assert result.name == "Green Lantern"
    assert result.country == "us"
    assert result.language == "en"
    assert len(result.active_issues) == 172
    assert result.active_issues[0] == "https://www.comics.org/api/issue/242700/?format=json"
    assert len(result.issue_descriptors) == 172
    assert result.issue_descriptors[0] == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.color == "color"
    assert result.dimensions == "standard Modern Age US"
    assert result.paper_stock == "glossy"
    assert result.binding == "saddle-stitched"
    assert result.publishing_format == "was ongoing series"
    assert result.notes == "Fourth series."
    assert result.year_began == 2005
    assert result.year_ended == 2011
    assert result.publisher == "https://www.comics.org/api/publisher/54/?format=json"


def test_series_fail(session: GrandComicsDatabase) -> None:
    """Test using the series endpoint with an invalid id."""
    with pytest.raises(ServiceError):
        session.get_series(id=-1)


def test_list_series(session: GrandComicsDatabase) -> None:
    """Test using the list_series endpoint with a valid search."""
    results = session.list_series()
    assert len(results) != 0
    result = next(x for x in results if x.id == 13519)
    assert result is not None

    assert result.api_url == "https://www.comics.org/api/series/13519/?format=json"
    assert result.name == "Green Lantern"
    assert result.country == "us"
    assert result.language == "en"
    assert len(result.active_issues) == 172
    assert result.active_issues[0] == "https://www.comics.org/api/issue/242700/?format=json"
    assert len(result.issue_descriptors) == 172
    assert result.issue_descriptors[0] == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.color == "color"
    assert result.dimensions == "standard Modern Age US"
    assert result.paper_stock == "glossy"
    assert result.binding == "saddle-stitched"
    assert result.publishing_format == "was ongoing series"
    assert result.notes == "Fourth series."
    assert result.year_began == 2005
    assert result.year_ended == 2011
    assert result.publisher == "https://www.comics.org/api/publisher/54/?format=json"


def test_list_series_empty(session: GrandComicsDatabase) -> None:
    """Test using the list_series endpoint with an invalid search."""
    results = session.list_series()
    assert len(results) == 0