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
      active_issues: A list of URLs for active issues in the series.
      api_url: Url to the resource in the GCD API.
      binding: The binding type of the series.
      color: The color information of the series.
      country: The country where the series is published.
      dimensions: The dimensions of the series.
      issue_descriptors:
      language: The language of the series.
      name: The name of the series.
      notes: Additional notes about the series.
      paper_stock:
      publisher: Url to the Publisher of this resource in the GCD API.
      publishing_format: The publishing format of the series.
      year_began: The year the series began.
      year_ended: The year the series ended.
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
