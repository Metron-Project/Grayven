"""The Series module.

This module provides the following classes:
- Series
"""

__all__ = ["Series"]

import re
from typing import Annotated, Optional

from pydantic import HttpUrl
from pydantic.functional_validators import BeforeValidator

from grayven.schemas import BaseModel, blank_is_none


class Series(BaseModel):
    """Contains fields for all Series.

    Attributes:
      active_issues:
      api_url:
      binding:
      color:
      country:
      dimensions:
      issue_descriptors:
      language:
      name:
      notes:
      paper_stock:
      publisher:
      publishing_format:
      year_began:
      year_ended:
    """

    active_issues: list[HttpUrl]
    api_url: HttpUrl
    binding: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    color: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    country: str
    dimensions: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    issue_descriptors: list[Annotated[Optional[str], BeforeValidator(blank_is_none)]]
    language: str
    name: str
    notes: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    paper_stock: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    publisher: HttpUrl
    publishing_format: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    year_began: int
    year_ended: Optional[int]

    @property
    def id(self) -> int:
        """The Series id, extracted from the `api_url`."""
        match = re.search(r"/series/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
