"""The Publisher module.

This module provides the following classes:
- Publisher
"""

__all__ = ["Publisher"]

import re
from datetime import datetime
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


class Publisher(BaseModel):
    """Contains fields for all Publishers.

    Attributes:
      api_url:
      brand_count:
      country:
      indicia_publisher_count:
      issue_count:
      modified:
      name:
      notes:
      series_count:
      url:
      year_began:
      year_began_uncertain:
      year_ended:
      year_ended_uncertain:
      year_overall_began:
      year_overall_began_uncertain:
      year_overall_ended:
      year_overall_ended_uncertain:
    """

    api_url: HttpUrl
    brand_count: int
    country: str
    indicia_publisher_count: int
    issue_count: int
    modified: datetime
    name: str
    notes: str  # or Blank
    series_count: int
    url: HttpUrl  # or Blank
    year_began: Optional[int]
    year_began_uncertain: bool
    year_ended: Optional[int]
    year_ended_uncertain: bool
    year_overall_began: Optional[int]
    year_overall_began_uncertain: bool
    year_overall_ended: Optional[int]
    year_overall_ended_uncertain: bool

    @property
    def id(self) -> int:
        """The Publisher id, extracted from the `api_url`."""
        match = re.search(r"/publisher/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
