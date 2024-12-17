"""The Issue module.

This module provides the following classes:
- BasicIssue
- Issue
- Story
- StoryType
"""

__all__ = ["BasicIssue", "Issue", "Story", "StoryType"]

import re
from datetime import date
from enum import Enum
from typing import Annotated, Optional

from pydantic import HttpUrl
from pydantic.functional_validators import BeforeValidator

from grayven.schemas import BaseModel, blank_is_none


class StoryType(str, Enum):
    """Enum to cover the different types of Stories an Issue can have."""

    ADVERTISEMENT = "advertisement"
    """"""
    COMIC_STORY = "comic story"
    """"""
    COVER = "cover"
    """"""
    IN_HOUSE_COLUMN = "in-house column"
    """"""


class Story(BaseModel):
    """Contains fields relating to the stories inside an Issue.

    Attributes:
      characters:
      colors:
      editing:
      feature:
      genre:
      inks:
      job_number:
      letters:
      notes:
      page_count:
      pencils:
      script:
      sequence_number:
      synopsis:
      title:
      type:
    """

    characters: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    colors: str
    editing: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    feature: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    genre: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    inks: str
    job_number: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    letters: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    notes: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    page_count: str
    pencils: str
    script: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    sequence_number: int
    synopsis: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    title: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    type: StoryType


class BasicIssue(BaseModel):
    """Contains fields for all Issues.

    Attributes:
      api_url:
      descriptor:
      page_count:
      price:
      publication_date:
      series:
      series_name:
      variant_of:
    """

    api_url: HttpUrl
    descriptor: str
    page_count: str
    price: str
    publication_date: str
    series: HttpUrl
    series_name: str
    variant_of: Optional[HttpUrl]

    @property
    def id(self) -> int:
        """The Issue id, extracted from the `api_url`."""
        match = re.search(r"/issue/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)


class Issue(BasicIssue):
    """Extends BasicIssue to include more details.

    Attributes:
      barcode:
      brand:
      cover:
      editing:
      indicia_frequency:
      indicia_publisher:
      isbn:
      notes:
      on_sale_date:
      rating:
      story_set:
    """

    barcode: str
    brand: str
    cover: HttpUrl
    editing: str
    indicia_frequency: str
    indicia_publisher: str
    isbn: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    notes: str
    on_sale_date: Optional[date]
    rating: str
    story_set: list[Story]
