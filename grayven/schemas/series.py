"""The Series module.

This module provides the following classes:
- Series
"""

__all__ = ["Series"]

import re
from typing import Annotated, Optional

from pydantic import Field, HttpUrl

from grayven.schemas import BaseModel


class Series(BaseModel):
    """Contains fields for all Series.

    Attributes:
      api_url: Url to the resource in the GCD API.
      name: The name of the series.
      country: The country where the series is published.
      language: The language of the series.
      active_issues: A list of URLs for active issues in the series.
      issue_descriptors:
      color: The color information of the series.
      dimensions: The dimensions of the series.
      paper_stock:
      binding: The binding type of the series.
      publishing_format: The publishing format of the series.
      notes: Additional notes about the series.
      year_began: The year the series began.
      year_ended: The year the series ended.
      publisher: Url to the Publisher of this resource in the GCD API.
    """

    api_url: HttpUrl
    name: Annotated[str, Field(max_length=255)]
    country: str
    language: str
    active_issues: list[HttpUrl]
    issue_descriptors: list[str]
    color: Annotated[str, Field(max_length=255)] = ""
    dimensions: Annotated[str, Field(max_length=255)] = ""
    paper_stock: Annotated[str, Field(max_length=255)] = ""
    binding: Annotated[str, Field(max_length=255)] = ""
    publishing_format: Annotated[str, Field(max_length=255)] = ""
    notes: str
    year_began: Annotated[int, Field(gt=-2147483648, lt=2147483647)]
    year_ended: Annotated[Optional[int], Field(gt=-2147483648, lt=2147483647)] = None
    publisher: HttpUrl

    @property
    def id(self) -> int:
        """The Series id, extracted from the `api_url` field."""
        if match := re.search(r"/series/(\d+)/", str(self.api_url)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)

    @property
    def publisher_id(self) -> int:
        """The Publisher id, extracted from the `publisher` field."""
        if match := re.search(r"/publisher/(\d+)/", str(self.api_url)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
