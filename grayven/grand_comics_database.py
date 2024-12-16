__all__ = ["GrandComicsDatabase"]

import platform
from json import JSONDecodeError
from typing import Any, Optional
from urllib.parse import urlencode

from httpx import HTTPStatusError, RequestError, TimeoutException, get
from pydantic import TypeAdapter, ValidationError
from ratelimit import limits, sleep_and_retry

from grayven import __version__
from grayven.exceptions import ServiceError
from grayven.schemas.issue import BasicIssue, Issue
from grayven.schemas.publisher import Publisher
from grayven.schemas.series import Series
from grayven.sqlite_cache import SQLiteCache

MINUTE = 60


class GrandComicsDatabase:
    API_URL = "https://www.comics.org/api"

    def __init__(self, timeout: int = 30, cache: Optional[SQLiteCache] = None):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"Grayven/{__version__}/{platform.system()}: {platform.release()}",
        }
        self.timeout = timeout
        self.cache = cache

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _perform_get_request(
        self, url: str, params: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if params is None:
            params = {}

        try:
            response = get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestError as err:
            raise ServiceError("Unable to connect to '%s'", url) from err
        except HTTPStatusError as err:
            try:
                if err.response.status_code == 404:
                    raise ServiceError(err.response.json()["detail"])
                raise ServiceError(err) from err
            except JSONDecodeError as err:
                raise ServiceError("Unable to parse response from '%s' as Json", url) from err
        except JSONDecodeError as err:
            raise ServiceError("Unable to parse response from '%s' as Json", url) from err
        except TimeoutException as err:
            raise ServiceError("Service took too long to respond") from err

    def _get_request(
        self, endpoint: str, params: Optional[dict[str, str]] = None, skip_cache: bool = False
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        params["format"] = "json"

        url = self.API_URL + endpoint + "/"
        cache_params = f"?{urlencode({k: params[k] for k in sorted(params)})}"
        cache_key = url + cache_params

        if self.cache and not skip_cache:
            cached_response = self.cache.select(key=cache_key)
            if cached_response:
                return cached_response
        response = self._perform_get_request(url=url, params=params)
        if self.cache and not skip_cache:
            self.cache.insert(key=cache_key, value=response)
        return response

    def _get_paged_request(
        self, endpoint: str, params: Optional[dict[str, str]] = None, max_results: int = 500
    ) -> list[dict[str, Any]]:
        if params is None:
            params = {}
        params["page"] = 1
        response = self._get_request(endpoint=endpoint, params=params)
        results = response["results"]
        while (
            response["results"] and len(results) < response["count"] and len(results) < max_results
        ):
            params["page"] += 1
            response = self._get_request(endpoint=endpoint, params=params)
            results.extend(response["results"])
        return results[:max_results]

    def list_publishers(self, max_results: int = 500) -> list[Publisher]:
        try:
            results = self._get_paged_request(endpoint="/publisher", max_results=max_results)
            return TypeAdapter(list[Publisher]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_publisher(self, id: int) -> Optional[Publisher]:  # noqa: A002
        try:
            result = self._get_request(endpoint=f"/publisher/{id}")
            return TypeAdapter(Publisher).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_series(
        self, name: Optional[str] = None, year: Optional[int] = None, max_results: int = 500
    ) -> list[Series]:
        try:
            if name is None:
                results = self._get_paged_request(endpoint="/series", max_results=max_results)
            elif year is None:
                results = self._get_paged_request(
                    endpoint=f"/series/name/{name}", max_results=max_results
                )
            else:
                results = self._get_paged_request(
                    endpoint=f"/series/name/{name}/year/{year}", max_results=max_results
                )
            return TypeAdapter(list[Series]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_series(self, id: int) -> Optional[Series]:  # noqa: A002
        try:
            result = self._get_request(endpoint=f"/series/{id}")
            return TypeAdapter(Series).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_issues(
        self,
        series_name: str,
        issue_number: int,
        year: Optional[int] = None,
        max_results: int = 500,
    ) -> list[BasicIssue]:
        try:
            if year is None:
                results = self._get_paged_request(
                    endpoint=f"/series/name/{series_name}/issue/{issue_number}",
                    max_results=max_results,
                )
            else:
                results = self._get_paged_request(
                    endpoint=f"/series/name/{series_name}/issue/{issue_number}/year/{year}",
                    max_results=max_results,
                )
            return TypeAdapter(list[BasicIssue]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_issue(self, id: int) -> Optional[Issue]:  # noqa: A002
        try:
            result = self._get_request(endpoint=f"/issue/{id}")
            return TypeAdapter(Issue).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err
