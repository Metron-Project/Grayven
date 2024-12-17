"""The Exceptions module.

This module provides the following classes:
- ServiceError
"""

__all__ = ["ServiceError"]


class ServiceError(Exception):
    """Class for any API errors."""
