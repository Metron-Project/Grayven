"""The Series module.

This module provides the following classes:
- Series
"""

__all__ = ["Series"]

import re
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


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
    binding: str
    color: str
    country: str
    dimensions: str
    issue_descriptors: list[str]
    language: str
    name: str
    notes: str  # or Blank
    paper_stock: str
    publisher: HttpUrl
    publishing_format: str
    year_began: int
    year_ended: Optional[int]

    @property
    def id(self) -> int:
        """The Series id, extracted from the `api_url`."""
        match = re.search(r"/series/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
