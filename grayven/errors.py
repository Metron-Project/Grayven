__all__ = ["AuthenticationError", "RateLimitError", "ServiceError"]


class ServiceError(Exception):
    """Class for any API errors."""


class AuthenticationError(ServiceError):
    """Class for any Authentication errors."""


class RateLimitError(ServiceError):
    """Class for any API Rate Limit errors."""
