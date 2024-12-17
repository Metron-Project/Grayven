"""grayven.schemas package entry file.

This module provides the following classes:
- BaseModel
"""

__all__ = ["BaseModel", "blank_is_none"]

from typing import Optional

from pydantic import BaseModel as PydanticModel


class BaseModel(
    PydanticModel,
    populate_by_name=True,
    str_strip_whitespace=True,
    validate_assignment=True,
    revalidate_instances="always",
    extra="forbid",
):
    """Base model for Grayven resources."""


def blank_is_none(value: str) -> Optional[str]:
    """Enforces blank strings to be None."""
    return value if value else None
