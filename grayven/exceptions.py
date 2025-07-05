"""The Exceptions module.

This module provides the following classes:
- ServiceError
"""

__all__ = ["RateLimitError", "ServiceError"]


class ServiceError(Exception):
    """Class for any API errors."""


class RateLimitError(Exception):
    """Class for any API errors."""
