__all__ = ["GrandComicsDatabase"]

import platform
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final, Literal, TypeVar

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
T = TypeVar("T")
HttpMethod = Literal["GET"]


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
        base_url: Root URL of the GCD API.
        user_agent: Value sent in the `User-Agent` request header.
        timeout: Set how long requests will wait for a response (in seconds).
        cache_path: Path to the SQLite cache file.
            If not provided, a default path will be used under ~/.cache/grayven/cache.sqlite
        cache_expiry: Duration for which cached responses are valid.
            Response cache-headers take precedence.
        ratelimit_path: Path to the SQLite ratelimit file.
            If not provided, a default path will be used under ~/.cache/grayven/ratelimits.sqlite
    """

    def __init__(
        self,
        email: str,
        password: str,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float = 20,
        cache_path: Path | None = None,
        cache_expiry: timedelta = timedelta(days=14),
        ratelimit_path: Path | None = None,
    ):
        self._base_url = base_url or "https://www.comics.org/api"
        self._session = CachedLimiterSession(
            backend=SQLiteCache(
                db_path=cache_path or (get_cache_root() / "cache.sqlite"), serializer="json"
            ),
            expire_after=cache_expiry,
            cache_control=cache_expiry != NEVER_EXPIRE,
            per_minute=20,
            per_hour=200,
            per_day=2_000,
            max_delay=timeout * 2,
            bucket_class=SQLiteBucket,
            bucket_kwargs={"path": ratelimit_path or (get_cache_root() / "ratelimits.sqlite")},
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

    def _request(
        self, method: HttpMethod, endpoint: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        url = f"{self._base_url}{endpoint}/"
        kwargs: dict[str, Any] = {"timeout": self._timeout}
        if params:
            kwargs["params"] = params
        try:
            response = self._session.request(method=method, url=url, **kwargs)
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
                    f"{status_code}: Unable to parse response from '{url}' as Json"
                ) from err
        except Timeout as err:
            raise ServiceError("Service took too long to respond") from err
        except RequestException as err:
            raise ServiceError(f"Unable to connect to '{url}'") from err
        except JSONDecodeError as err:
            raise ServiceError(f"Unable to parse response from '{url}' as Json") from err

    @staticmethod
    def _convert(data: dict[str, Any], type_: type[T]) -> T:
        try:
            return TypeAdapter(type_).validate_python(data)
        except ValidationError as err:
            raise ServiceError(err) from err

    def _paginate(
        self, endpoint: str, params: dict[str, str] | None = None, max_results: int | None = None
    ) -> list[dict[str, Any]]:
        params = params or {}
        page = int(params.get("page", "1"))
        results = []
        while True:
            params["page"] = str(page)
            response = self._request(method="GET", endpoint=endpoint, params=params)
            results.extend(response["results"])
            if max_results is not None and len(results) >= max_results:
                return results[:max_results]
            if response["next"] is None:
                return results
            page += 1

    def _get_item(self, endpoint: str, type_: type[T]) -> T:
        return self._convert(data=self._request(method="GET", endpoint=endpoint), type_=type_)

    def _get_list(
        self,
        endpoint: str,
        type_: type[T],
        params: dict[str, str] | None = None,
        max_results: int | None = None,
    ) -> list[T]:
        data = self._paginate(endpoint=endpoint, params=params, max_results=max_results)
        return [self._convert(data=x, type_=type_) for x in data]

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
        return self._get_item(endpoint=f"/issue/{issue_id}", type_=Issue)

    def list_onsale_weekly_issues(
        self, year: int, week: int, max_results: int | None = 500
    ) -> list[BasicIssue]:
        """Request a list of issues on sale in a given ISO week.

        Args:
            year: The ISO year (4-digit year).
            week: The ISO week number (1-53).
            max_results: If given, return at most this many results.

        Returns:
            List of BasicIssue objects representing issues that went on sale during the given week.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        return self._get_list(
            endpoint=f"/issue/on_sale_weekly/{year}/week/{week}",
            type_=BasicIssue,
            max_results=max_results,
        )

    def list_publishers(self, max_results: int | None = 500) -> list[Publisher]:
        """Request a list of Publishers.

        Args:
            max_results: If given, return at most this many results.

        Returns:
            A list of Publisher objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        return self._get_list(endpoint="/publisher", type_=Publisher, max_results=max_results)

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
        return self._get_item(endpoint=f"/publisher/{publisher_id}", type_=Publisher)

    def list_series(
        self, name: str | None = None, year: int | None = None, max_results: int | None = 500
    ) -> list[Series]:
        """Request a list of Series.

        Args:
            name: Filter the results using the series name.
            year: Filter the results using the series beginning year (Requires name to be passed).
            max_results: If given, return at most this many results.

        Returns:
            A list of Series objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        if name is None:
            return self._get_list(endpoint="/series", type_=Series, max_results=max_results)
        if year is None:
            return self._get_list(
                endpoint=f"/series/name/{name}", type_=Series, max_results=max_results
            )
        return self._get_list(
            endpoint=f"/series/name/{name}/year/{year}", type_=Series, max_results=max_results
        )

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
        return self._get_item(endpoint=f"/series/{series_id}", type_=Series)

    def list_issues(
        self,
        series_name: str,
        issue_number: int,
        year: int | None = None,
        max_results: int | None = 500,
    ) -> list[BasicIssue]:
        """Request a list of Issues.

        Args:
            series_name: The name of the series to filter issues from.
            issue_number: The number to filter issues by.
            year: Filter the results using the issue year via its key_date.
            max_results: If given, return at most this many results.

        Returns:
            A list of Issue objects.

        Raises:
            ServiceError: If the API response is invalid or validation fails.
            AuthenticationError: If credentials are invalid.
            RateLimitError: If the API rate limit is exceeded.
        """
        if year is None:
            return self._get_list(
                endpoint=f"/series/name/{series_name}/issue/{issue_number}",
                type_=BasicIssue,
                max_results=max_results,
            )
        return self._get_list(
            endpoint=f"/series/name/{series_name}/issue/{issue_number}/year/{year}",
            type_=BasicIssue,
            max_results=max_results,
        )
