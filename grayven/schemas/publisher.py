"""The Publisher module.

This module provides the following classes:
- Publisher
"""

__all__ = ["Publisher"]

import re
from datetime import datetime
from typing import Annotated

from pydantic import Field, HttpUrl
from pydantic.functional_validators import BeforeValidator

from grayven.schemas import BaseModel, blank_is_none


class Publisher(BaseModel):
    """Contains fields for all Publishers.

    Attributes:
      api_url: Url to the resource in the GCD API.
      country: The country where the publisher is based.
      modified: The date and time when the publisher's information was last modified.
      name: The name of the publisher.
      year_began: The year the publisher began.
      year_ended: The year the publisher ended.
      year_began_uncertain:
      year_ended_uncertain:
      year_overall_began:
      year_overall_ended:
      year_overall_began_uncertain:
      year_overall_ended_uncertain:
      notes: Additional notes about the publisher.
      url: Url to the resource in the GCD.
      brand_count: The number of brands associated with the publisher.
      indicia_publisher_count: The number of indicia publishers associated with the publisher.
      series_count: The number of series published by the publisher.
      issue_count: The total number of issues published.
    """

    api_url: HttpUrl
    country: str
    modified: datetime
    name: Annotated[str, Field(max_length=255)]
    year_began: Annotated[int | None, Field(gt=-2147483648, lt=2147483647)] = None
    year_ended: Annotated[int | None, Field(gt=-2147483648, lt=2147483647)] = None
    year_began_uncertain: bool = False
    year_ended_uncertain: bool = False
    year_overall_began: Annotated[int | None, Field(gt=-2147483648, lt=2147483647)] = None
    year_overall_ended: Annotated[int | None, Field(gt=-2147483648, lt=2147483647)] = None
    year_overall_began_uncertain: bool = False
    year_overall_ended_uncertain: bool = False
    notes: str
    url: Annotated[HttpUrl | None, Field(max_length=255), BeforeValidator(blank_is_none)] = None
    brand_count: Annotated[int, Field(gt=-2147483648, lt=2147483647)] = 0
    indicia_publisher_count: Annotated[int, Field(gt=-2147483648, lt=2147483647)] = 0
    series_count: Annotated[int, Field(gt=-2147483648, lt=2147483647)] = 0
    issue_count: Annotated[int, Field(gt=-2147483648, lt=2147483647)] = 0

    @property
    def id(self) -> int:
        """The Publisher id, extracted from the `api_url` field."""
        if match := re.search(r"/publisher/(\d+)/", str(self.api_url)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)
