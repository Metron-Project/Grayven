__all__ = ["GrandComicsDatabase"]

import platform
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from pydantic import TypeAdapter, ValidationError
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, JSONDecodeError, RequestException, Timeout
from requests.sessions import Session
from requests_cache import NEVER_EXPIRE, CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, SQLiteBucket

from grayven import __version__, get_cache_root
from grayven.errors import AuthenticationError, RateLimitError, ServiceError
from grayven.schemas import BasicIssue, Issue, Publisher, Series

SECONDS_PER_MINUTE: Final[int] = 60
SECONDS_PER_HOUR: Final[int] = 3_600


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


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
        cache: Path to the SQLite cache file.
            If not provided, a default path will be used under <cache-root>/cache.sqlite
        base_url: Root URL of the GCD API.
        user_agent: Value sent in the `User-Agent` request header.
        timeout: Set how long requests will wait for a response (in seconds).
        cache_expiry: Duration for which cached responses are valid.
            Response cache-headers take precedence.
    """

    def __init__(
        self,
        email: str,
        password: str,
        cache: Path | None = None,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float = 20,
        cache_expiry: timedelta = timedelta(days=14),
    ):
        self._base_url = base_url or "https://www.comics.org/api"
        self._session = CachedLimiterSession(
            backend=SQLiteCache(
                db_path=cache or (get_cache_root() / "cache.sqlite"), serializer="json"
            ),
            expire_after=cache_expiry,
            cache_control=cache_expiry != NEVER_EXPIRE,
            per_minute=20,
            per_hour=200,
            per_day=2_000,
            max_delay=timeout * 2,
            bucket_class=SQLiteBucket,
            per_host=False,
            bucket_name="grand-comics-database",
        )
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": user_agent
                or f"Grayven/{__version__} ({platform.system()}: {platform.release()}; Python v{platform.python_version()})",  # noqa: E501
            }
        )
        self._session.auth = HTTPBasicAuth(username=email, password=password)
        self._timeout = timeout

    def _get_request(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        params: dict[str, str] = params or {}
        try:
            response = self._session.get(
                url=f"{self._base_url}{endpoint}/", params=params, timeout=self._timeout
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as err:
            status_code = (
                HTTPStatus.INTERNAL_SERVER_ERROR
                if err.response is None
                else err.response.status_code
            )
            try:
                response = {} if err.response is None else err.response.json()
                if status_code == HTTPStatus.UNAUTHORIZED:
                    raise AuthenticationError(response["detail"]) from err
                if status_code == HTTPStatus.NOT_FOUND:
                    raise ServiceError(response["detail"]) from err
                if status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    raise RateLimitError(
                        f"Too Many API Requests: Need to wait {format_time(seconds=0 if err.response is None else err.response.headers.get('Retry-After', 0))}s."  # noqa: E501
                    ) from err
                raise ServiceError(f"{status_code}: {response}") from err
            except JSONDecodeError as err:
                raise ServiceError(
                    f"{status_code}: Unable to parse response from '{self._base_url}{endpoint}/' as Json"  # noqa: E501
                ) from err
        except Timeout as err:
            raise ServiceError("Service took too long to respond") from err
        except RequestException as err:
            raise ServiceError(f"Unable to connect to '{self._base_url}{endpoint}/'") from err
        except JSONDecodeError as err:
            raise ServiceError(
                f"Unable to parse response from '{self._base_url}{endpoint}/' as Json"
            ) from err

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

    def get_issue(self, issue_id: int) -> Issue:
        """Request an Issue using its id.

        Args:
            issue_id: The Issue id.

        Returns:
            A Issue object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/issue/{issue_id}")
            return TypeAdapter(Issue).validate_python(result)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_onsale_weekly_issues(
        self, year: int, week: int, max_results: int = 500
    ) -> list[BasicIssue]:
        """Request a list of issues on sale in a given ISO week.

        Args:
            year: The ISO year (4-digit year).
            week: The ISO week number (1-53).
            max_results: Maximum number of results to retrieve.

        Returns:
            List of BasicIssue objects representing issues that went on sale during the given week.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            results = self._fetch_list(
                endpoint=f"/issue/on_sale_weekly/{year}/week/{week}", max_results=max_results
            )
            return TypeAdapter(list[BasicIssue]).validate_python(results)
        except ValidationError as err:
            raise ServiceError(err) from err

    def list_publishers(self, max_results: int = 500) -> list[Publisher]:
        """Request a list of Publishers.

        Args:
            max_results: Maximum number of results to retrieve.

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

    def get_publisher(self, publisher_id: int) -> Publisher:
        """Request a Publisher using its id.

        Args:
            publisher_id: The Publisher id.

        Returns:
            A Publisher object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/publisher/{publisher_id}")
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
            max_results: Maximum number of results to retrieve.

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

    def get_series(self, series_id: int) -> Series:
        """Request a Series using its id.

        Args:
            series_id: The Series id.

        Returns:
            A Series object.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        try:
            result = self._fetch_item(endpoint=f"/series/{series_id}")
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
            max_results: Maximum number of results to retrieve.

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
