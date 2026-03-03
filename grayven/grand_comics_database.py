__all__ = ["GrandComicsDatabase"]

import logging
import platform
from json import JSONDecodeError
from typing import Any, Final
from urllib.parse import urlencode

from httpx import BasicAuth, Client, HTTPStatusError, RequestError, TimeoutException, codes
from pydantic import TypeAdapter, ValidationError
from pyrate_limiter import AbstractBucket, Duration, Limiter, Rate, SQLiteBucket
from pyrate_limiter.extras.httpx_limiter import RateLimiterTransport

from grayven import __version__
from grayven.cache import SQLiteCache
from grayven.errors import AuthenticationError, RateLimitError, ServiceError
from grayven.schemas import BasicIssue, Issue, Publisher, Series

# Constants
LOGGER = logging.getLogger(__name__)
SECONDS_PER_MINUTE: Final[int] = 60
SECONDS_PER_HOUR: Final[int] = 3_600
RATELIMIT_BUCKET: Final[AbstractBucket] = SQLiteBucket.init_from_file(
    [Rate(20, Duration.MINUTE), Rate(200, Duration.HOUR), Rate(2_000, Duration.DAY)]
)


def format_time(seconds: str | float) -> str:
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
        email: The user's GCD email address, which is used for authentication.
        password: The user's GCD password, which is used for authentication.
        cache: SQLiteCache to use if set.
        base_url: Root URL of the GCD API.
        user_agent: Value sent in the `User-Agent` request header.
        timeout: Set how long requests will wait for a response (in seconds).
        limiter: Set a custom limiter, used for testing.
    """

    def __init__(
        self,
        email: str,
        password: str,
        cache: SQLiteCache | None,
        base_url: str = "https://www.comics.org/api",
        user_agent: str | None = None,
        timeout: float = 30,
        limiter: Limiter = Limiter(RATELIMIT_BUCKET),  # noqa: B008
    ):
        self._base_url = base_url
        self._client = Client(
            base_url=self._base_url,
            headers={
                "Accept": "application/json",
                "User-Agent": user_agent
                or f"Grayven/{__version__} ({platform.system()}: {platform.release()}; Python v{platform.python_version()})",  # noqa: E501
            },
            auth=BasicAuth(username=email, password=password),
            params={"format": "json"},
            timeout=timeout,
            transport=RateLimiterTransport(limiter),
        )
        self._cache = cache

    def _perform_get_request(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        params: dict[str, str] = params or {}

        try:
            response = self._client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except RequestError as err:
            raise ServiceError(f"Unable to connect to '{self._base_url}{endpoint}'") from err
        except HTTPStatusError as err:
            status_code = err.response.status_code
            try:
                if err.response.status_code == codes.UNAUTHORIZED:
                    raise AuthenticationError(err.response.json()["detail"]) from err
                if err.response.status_code == codes.NOT_FOUND:
                    raise ServiceError(err.response.json()["detail"]) from err
                if err.response.status_code == codes.TOO_MANY_REQUESTS:
                    raise RateLimitError(
                        f"Too Many API Requests: Need to wait {format_time(seconds=err.response.headers.get('Retry-After', 0))}."  # noqa: E501
                    ) from err
                raise ServiceError(err.response.json()) from err
            except JSONDecodeError as err:
                raise ServiceError(
                    f"{status_code}: Unable to parse response from '{self._base_url}{endpoint}' as Json"  # noqa: E501
                ) from err
        except JSONDecodeError as err:
            raise ServiceError(
                f"Unable to parse response from '{self._base_url}{endpoint}' as Json"
            ) from err
        except TimeoutException as err:
            raise ServiceError("Service took too long to respond") from err

    def _get_request(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        params: dict[str, str] = params or {}
        url = f"{self._base_url}{endpoint}/"
        cache_params = f"?{urlencode({k: params[k] for k in sorted(params)})}"
        cache_key = url + cache_params

        if self._cache and (cache_data := self._cache.select(url=cache_key)):
            return cache_data.response
        response = self._perform_get_request(endpoint=endpoint + "/", params=params)
        if self._cache:
            self._cache.insert(url=cache_key, response=response)
        return response

    def _fetch_item(self, endpoint: str) -> dict[str, Any]:
        return self._get_request(endpoint=endpoint)

    def _fetch_list(
        self, endpoint: str, max_results: int, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = params or {}
        results: list[dict[str, Any]] = []
        page = int(params.get("page", "1"))
        while True:
            response = self._get_request(endpoint=endpoint, params={**params, "page": str(page)})
            results.extend(response["results"])
            page += 1
            if response["next"] is None or len(results) >= max_results:
                break
        return results[:max_results]

    def get_issue(self, id: int) -> Issue:  # noqa: A002
        """Request an Issue using its id.

        Args:
            id: The Issue id.

        Returns:
            A Issue object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/issue/{id}")
            return TypeAdapter(Issue).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_publishers(self, max_results: int = 500) -> list[Publisher]:
        """Request a list of Publishers.

        Args:
            max_results: Limits the amount of results looked up and returned.

        Returns:
            A list of Publisher objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            results = self._fetch_list(endpoint="/publisher", max_results=max_results)
            return TypeAdapter(list[Publisher]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_publisher(self, id: int) -> Publisher:  # noqa: A002
        """Request a Publisher using its id.

        Args:
            id: The Publisher id.

        Returns:
            A Publisher object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/publisher/{id}")
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
            max_results: Limits the amount of results looked up and returned.

        Returns:
            A list of Series objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            if name is None:
                results = self._fetch_list(endpoint="/series", max_results=max_results)
            elif year is None:
                results = self._fetch_list(endpoint=f"/series/name/{name}", max_results=max_results)
            else:
                results = self._fetch_list(
                    endpoint=f"/series/name/{name}/year/{year}", max_results=max_results
                )
            return TypeAdapter(list[Series]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def get_series(self, id: int) -> Series:  # noqa: A002
        """Request a Series using its id.

        Args:
            id: The Series id.

        Returns:
            A Series object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/series/{id}")
            return TypeAdapter(Series).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_issues(
        self, series_name: str, issue_number: int, year: int | None = None, max_results: int = 500
    ) -> list[BasicIssue]:
        """Request a list of Issues.

        Args:
            series_name: The name of the series to filter issues from.
            issue_number: The number to filter issues by.
            year: Filter the results using the issue year via its key_date.
            max_results: Limits the amount of results looked up and returned.

        Returns:
            A list of Issue objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            if year is None:
                results = self._fetch_list(
                    endpoint=f"/series/name/{series_name}/issue/{issue_number}",
                    max_results=max_results,
                )
            else:
                results = self._fetch_list(
                    endpoint=f"/series/name/{series_name}/issue/{issue_number}/year/{year}",
                    max_results=max_results,
                )
            return TypeAdapter(list[BasicIssue]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err
