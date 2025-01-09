"""The Issue test module.

This module contains tests for Issue and BasicIssue objects.
"""

from datetime import date
from decimal import Decimal

import pytest
from pytest_httpx import HTTPXMock

from grayven.exceptions import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase
from grayven.schemas.issue import Issue, StoryType


@pytest.fixture
def issue_no_page_json() -> dict[str, any]:
    """Simple fixture for issue with no page."""
    return {
        "api_url": "https://www.comics.org/api/issue/2698986/?format=json",
        "series_name": "Cruel Kingdom (2025 series)",
        "descriptor": "1",
        "publication_date": "January 2025",
        "price": "4.99 USD",
        "page_count": None,
        "editing": "",
        "indicia_publisher": "Oni-Lion Forge Publishing Group, LLC",
        "brand": "EC An Entertaining Comic; Oni Press [eye]",
        "isbn": "",
        "barcode": "64985600823700111",
        "rating": "",
        "on_sale_date": "2025-01-08",
        "indicia_frequency": "",
        "notes": "",
        "variant_of": None,
        "series": "https://www.comics.org/api/series/219801/?format=json",
        "story_set": [],
        "cover": "https://files1.comics.org//img/gcd/covers_by_id/1743/w400/1743127.jpg",
    }


def test_issue_no_page(httpx_mock: HTTPXMock, issue_no_page_json: dict[str, any]) -> None:
    """Test issue with no page count."""
    session = GrandComicsDatabase()  # We don't want to cache these results
    httpx_mock.add_response(json=issue_no_page_json)
    result = session.get_issue(2698986)
    assert isinstance(result, Issue)
    assert result.page_count is None
    assert result.descriptor == "1"
    assert result.publication_date == "January 2025"


def test_issue(session: GrandComicsDatabase) -> None:
    """Test using the issue endpoint with a valid id."""
    result = session.get_issue(id=242700)
    assert result is not None
    assert result.id == 242700

    assert str(result.api_url) == "https://www.comics.org/api/issue/242700/?format=json"
    assert result.series_name == "Green Lantern (2005 series)"
    assert result.descriptor == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.publication_date == "July 2005"
    assert result.price == "3.50 USD; 4.75 CAD"
    assert result.page_count == Decimal("48")
    assert (
        result.editing
        == "Peter J. Tomasi (credited as  Peter Tomasi) (editor); Harvey Richards (credited) (assistant editor); Dan DiDio (credited) (executive editor); Paul Levitz (credited) (publisher)"  # noqa: E501
    )
    assert result.indicia_publisher == "DC Comics"
    assert result.brand == "DC [bullet]"
    assert result.isbn is None
    assert result.barcode == "76194124438900111"
    assert result.rating == "Approved by the Comics Code Authority"
    assert result.on_sale_date == date(2005, 5, 25)
    assert result.indicia_frequency == "monthly"
    assert result.variant_of is None
    assert str(result.series) == "https://www.comics.org/api/series/13519/?format=json"
    assert len(result.story_set) == 4
    assert result.story_set[0].type == StoryType.COVER
    assert result.story_set[0].title is None
    assert result.story_set[0].feature == "Green Lantern"
    assert result.story_set[0].sequence_number == 0
    assert result.story_set[0].page_count == Decimal("1")
    assert result.story_set[0].script is None
    assert result.story_set[0].pencils == "Carlos Pacheco (credited) (signed as Pacheco [scratch])"
    assert result.story_set[0].inks == "Jesús Merino (credited) (signed as Merino)"
    assert result.story_set[0].colors == "Peter Steigerwald (credited) (signed as Peter S:)"
    assert result.story_set[0].letters is None
    assert result.story_set[0].editing is None
    assert result.story_set[0].job_number is None
    assert result.story_set[0].genre == "superhero"
    assert result.story_set[0].characters == "Green Lantern [Hal Jordan]"
    assert result.story_set[0].synopsis is None
    assert result.story_set[0].notes is None
    assert (
        str(result.cover) == "https://files1.comics.org//img/gcd/covers_by_id/224/w400/224124.jpg"
    )


def test_issue_fail(session: GrandComicsDatabase) -> None:
    """Test using the issue endpoint with an invalid id."""
    with pytest.raises(ServiceError):
        session.get_issue(id=-1)


def test_list_issues(session: GrandComicsDatabase) -> None:
    """Test using the list_issues endpoint with a valid search."""
    results = session.list_issues(series_name="Green Lantern", issue_number=1, year=2005)
    assert len(results) == 6
    result = next(iter(x for x in results if x.id == 242700), None)
    assert result is not None

    assert str(result.api_url) == "https://www.comics.org/api/issue/242700/?format=json"
    assert result.series_name == "Green Lantern (2005 series)"
    assert result.descriptor == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.publication_date == "July 2005"
    assert result.price == "3.50 USD; 4.75 CAD"
    assert result.page_count == Decimal("48")
    assert result.variant_of is None
    assert str(result.series) == "https://www.comics.org/api/series/13519/?format=json"


def test_list_issue_invalid_series(session: GrandComicsDatabase) -> None:
    """Test using the list_issues endpoint with an invalid series_name."""
    results = session.list_issues(series_name="invalid", issue_number=1)
    assert len(results) == 0


def test_list_issue_invalid_number(session: GrandComicsDatabase) -> None:
    """Test using the list_issues endpoint with an invalid issue_number."""
    results = session.list_issues(series_name="Green Lantern", issue_number=-1)
    assert len(results) == 0
