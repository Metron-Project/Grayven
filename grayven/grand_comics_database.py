"""The GrandComicsDatabase module.

This module provides the following classes:
- GrandComicsDatabase
"""

__all__ = ["GrandComicsDatabase"]

import platform
from json import JSONDecodeError
from typing import Any, ClassVar, Final
from urllib.parse import urlencode

from httpx import Client, HTTPStatusError, RequestError, TimeoutException, codes
from pydantic import TypeAdapter, ValidationError
from pyrate_limiter import Duration, Limiter, Rate, SQLiteBucket

from grayven import __version__
from grayven.exceptions import RateLimitError, ServiceError
from grayven.schemas.issue import BasicIssue, Issue
from grayven.schemas.publisher import Publisher
from grayven.schemas.series import Series
from grayven.sqlite_cache import SQLiteCache

# Constants
GCD_MINUTE_RATE: Final[int] = 20  # Let's use this so we don't hammer their server per minute
GCD_HOUR_RATE: Final[int] = 200
GCD_DAY_RATE: Final[int] = 2_0000
SECONDS_PER_HOUR: Final[int] = 3_600
SECONDS_PER_MINUTE: Final[int] = 60


def rate_mapping(*arg: Any, **kwargs: Any) -> tuple[str, int]:
    return "gcd", 1


def format_time(seconds: str | float) -> str:
    """Format seconds into a verbose human-readable time string.

    Args:
        seconds (int or float): Number of seconds to format

    Returns:
        str: Formatted time string (e.g., "2 hours, 30 minutes, 45 seconds")
    """
    total_seconds = int(seconds)

    if total_seconds < 0:
        return "0 seconds"

    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    remaining_seconds = total_seconds % SECONDS_PER_MINUTE

    parts = []

    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if remaining_seconds > 0 or not parts:
        parts.append(f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}")

    return ", ".join(parts)


class GrandComicsDatabase:
    """Class with functionality to request GCD API endpoints.

    Args:
      cache: SQLiteCache to use if set.
    """

    _minute_rate = Rate(GCD_MINUTE_RATE, Duration.MINUTE)
    _hour_rate = Rate(GCD_HOUR_RATE, Duration.HOUR)
    _daily_rate = Rate(GCD_DAY_RATE, Duration.DAY)
    _rates: ClassVar[list[Rate]] = [_minute_rate, _hour_rate, _daily_rate]
    _bucket = SQLiteBucket.init_from_file(_rates)  # Save between sessions
    # Can a `BucketFullException` be raised when used as a decorator?
    _limiter = Limiter(_bucket, raise_when_fail=False, max_delay=Duration.DAY)
    decorator = _limiter.as_decorator()

    def __init__(
        self, email: str, password: str, timeout: int = 30, cache: SQLiteCache | None = None
    ):
        self._client = Client(
            base_url="https://www.comics.org/api",
            headers={
                "Accept": "application/json",
                "User-Agent": f"Grayven/{__version__}/{platform.system()}: {platform.release()}",
            },
            auth=(email, password),
            timeout=timeout,
        )
        self.cache = cache

    @decorator(rate_mapping)
    def _perform_get_request(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Make GET request to GCD API endpoint.

        Args:
          endpoint: The endpoint to request information from.
          params: Parameters to add to the request.

        Returns:
          Json response from the GCD API.

        Raises:
          RateLimitError: If the API rate limit is exceeded.
          ServiceError: If there is an issue with the request or response from the GCD API.
        """
        if params is None:
            params = {}

        try:
            response = self._client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except RequestError as err:
            raise ServiceError("Unable to connect to '%s'", err.request.url.path) from err
        except HTTPStatusError as err:
            try:
                if err.response.status_code == codes.NOT_FOUND:
                    raise ServiceError(err.response.json()["detail"])
                if err.response.status_code == codes.TOO_MANY_REQUESTS:
                    period = format_time(err.response.headers["Retry-After"])
                    raise RateLimitError("Too Many API Requests: Need to wait %s.", period)
                raise ServiceError(err) from err
            except JSONDecodeError as err:
                raise ServiceError("Unable to parse response as Json") from err
        except JSONDecodeError as err:
            raise ServiceError("Unable to parse response from as Json") from err
        except TimeoutException as err:
            raise ServiceError("Service took too long to respond") from err

    def _get_request(
        self, endpoint: str, params: dict[str, str] | None = None, skip_cache: bool = False
    ) -> dict[str, Any]:
        """Check cache or make GET request to GCD API endpoint.

        Args:
          endpoint: The endpoint to request information from.
          params: Parameters to add to the request.
          skip_cache: Skip reading and writing to cache.

        Returns:
          Json response from the GCD API.

        Raises:
          ServiceError: If there is an issue with the request or response from the GCD API.
        """
        if params is None:
            params = {}
        params["format"] = "json"

        endpoint += "/"
        cache_params = f"?{urlencode({k: params[k] for k in sorted(params)})}"
        cache_key = endpoint + cache_params

        if self.cache and not skip_cache:
            cached_response = self.cache.select(query=cache_key)
            if cached_response:
                return cached_response
        response = self._perform_get_request(endpoint=endpoint, params=params)
        if self.cache and not skip_cache:
            self.cache.insert(query=cache_key, response=response)
        return response

    def _get_paged_request(
        self, endpoint: str, params: dict[str, str] | None = None, max_results: int = 500
    ) -> list[dict[str, Any]]:
        """Get results from paged requests.

        Args:
          endpoint: The endpoint to request information from.
          params: Parameters to add to the request.
          max_results: Limits the amount of results looked up and returned.

        Returns:
          A list of Json response results.
        """
        if params is None:
            params = {}
        params["page"] = str(1)
        response = self._get_request(endpoint=endpoint, params=params)
        results = response["results"]
        while (
            response["results"] and len(results) < response["count"] and len(results) < max_results
        ):
            params["page"] = str(int(params["page"]) + 1)
            response = self._get_request(endpoint=endpoint, params=params)
            results.extend(response["results"])
        return results[:max_results]

    def list_publishers(self, max_results: int = 500) -> list[Publisher]:
        """Request a list of Publishers.

        Args:
          max_results: Limits the amount if results looked up and returned.

        Returns:
          A list of Publisher objects.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
        try:
            results = self._get_paged_request(endpoint="/publisher", max_results=max_results)
            return TypeAdapter(list[Publisher]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_publisher(self, id: int) -> Publisher | None:  # noqa: A002
        """Request a Publisher using its id.

        Args:
          id: The Publisher id.

        Returns:
          A Publisher object or None if not found.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
        try:
            result = self._get_request(endpoint=f"/publisher/{id}")
            return TypeAdapter(Publisher).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_series(
        self, name: str | None = None, year: int | None = None, max_results: int = 500
    ) -> list[Series]:
        """Request a list of Series.

        Args:
          name: Filter the results using the series name.
          year: Filter the results using the series beginning year (Requires name to be passed).
          max_results: Limits the amount if results looked up and returned.

        Returns:
          A list of Series objects.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
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

    def get_series(self, id: int) -> Series | None:  # noqa: A002
        """Request a Series using its id.

        Args:
          id: The Series id.

        Returns:
          A Series object or None if not found.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
        try:
            result = self._get_request(endpoint=f"/series/{id}")
            return TypeAdapter(Series).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_issues(
        self, series_name: str, issue_number: int, year: str | None = None, max_results: int = 500
    ) -> list[BasicIssue]:
        """Request a list of Issues.

        Args:
          series_name: The name of the series to filter issues from.
          issue_number: The number to filter issues by.
          year: Filter the results using the issue year via its key_date.
          max_results: Limits the amount if results looked up and returned.

        Returns:
          A list of Issue objects.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
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

    def get_issue(self, id: int) -> Issue | None:  # noqa: A002
        """Request an Issue using its id.

        Args:
          id: The Issue id.

        Returns:
          A Issue object or None if not found.

        Raises:
          ServiceError: If there is an issue with validating the response.
        """
        try:
            result = self._get_request(endpoint=f"/issue/{id}")
            return TypeAdapter(Issue).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err
