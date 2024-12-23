"""The Publisher module.

This module provides the following classes:
- Publisher
"""

__all__ = ["Publisher"]

import re
from datetime import datetime
from typing import Annotated, Optional

from pydantic import HttpUrl
from pydantic.functional_validators import BeforeValidator

from grayven.schemas import BaseModel, blank_is_none


class Publisher(BaseModel):
    """Contains fields for all Publishers.

    Attributes:
      api_url: Url to the resource in the GCD API.
      brand_count: The number of brands associated with the publisher.
      country: The country where the publisher is based.
      indicia_publisher_count: The number of indicia publishers associated with the publisher.
      issue_count: The total number of issues published.
      modified: The date and time when the publisher's information was last modified.
      name: The name of the publisher.
      notes: Additional notes about the publisher.
      series_count: The number of series published by the publisher.
      url: Url to the resource in the GCD.
      year_began: The year the publisher began.
      year_began_uncertain:
      year_ended: The year the publisher ended.
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
    notes: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    series_count: int
    url: Annotated[Optional[HttpUrl], BeforeValidator(blank_is_none)]
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
        """The Publisher id, extracted from the `api_url` field."""
        if match := re.search(r"/publisher/(\d+)/", str(self.api_url)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
