import pytest
from responses import RequestsMock as Mocker

from grayven.errors import ServiceError
from grayven.grand_comics_database import GrandComicsDatabase


def test_series(session: GrandComicsDatabase) -> None:
    result = session.get_series(series_id=13519)
    assert result is not None
    assert result.id == 13519

    assert str(result.api_url) == "https://www.comics.org/api/series/13519/"
    assert result.name == "Green Lantern"
    assert result.country == "us"
    assert result.language == "en"
    assert len(result.active_issues) == 181
    assert str(result.active_issues[0]) == "https://www.comics.org/api/issue/242700/"
    assert len(result.issue_descriptors) == 181
    assert result.issue_descriptors[0] == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.color == "color"
    assert result.dimensions == "standard Modern Age US"
    assert result.paper_stock == "glossy"
    assert result.binding == "saddle-stitched"
    assert result.publishing_format == "was ongoing series"
    assert result.notes == "Fourth series."
    assert result.year_began == 2005
    assert result.year_ended == 2011
    assert str(result.publisher) == "https://www.comics.org/api/publisher/54/"


def test_series_fail(mock_session: GrandComicsDatabase) -> None:
    with Mocker(assert_all_requests_are_fired=True) as mock:
        url = "https://comics.mock/api/series/-1/"
        mock.get(url=url, status=404, json={"detail": "Not found."})
        with pytest.raises(ServiceError):
            mock_session.get_series(series_id=-1)
        mock.assert_call_count(url, 1)


def test_list_series(session: GrandComicsDatabase) -> None:
    results = session.list_series(name="Green Lantern", year=2005)
    assert len(results) == 6
    result = next(iter(x for x in results if x.id == 13519), None)
    assert result is not None

    assert str(result.api_url) == "https://www.comics.org/api/series/13519/"
    assert result.name == "Green Lantern"
    assert result.country == "us"
    assert result.language == "en"
    assert len(result.active_issues) == 181
    assert str(result.active_issues[0]) == "https://www.comics.org/api/issue/242700/"
    assert len(result.issue_descriptors) == 181
    assert result.issue_descriptors[0] == "1 [Direct Sales - Carlos Pacheco / Jesus Merino Cover]"
    assert result.color == "color"
    assert result.dimensions == "standard Modern Age US"
    assert result.paper_stock == "glossy"
    assert result.binding == "saddle-stitched"
    assert result.publishing_format == "was ongoing series"
    assert result.notes == "Fourth series."
    assert result.year_began == 2005
    assert result.year_ended == 2011
    assert str(result.publisher) == "https://www.comics.org/api/publisher/54/"


def test_list_series_empty(session: GrandComicsDatabase) -> None:
    results = session.list_series(name="invalid")
    assert len(results) == 0


def test_list_series_without_year(session: GrandComicsDatabase) -> None:
    results = session.list_series(year=2005)
    assert len(results) == 500
