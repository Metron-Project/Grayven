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
from decimal import Decimal
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
      characters: The characters in the story.
      colors: The color credits for the story.
      editing: The editing credits for the story.
      feature:
      genre: The genre of the story.
      inks: The ink credits for the story.
      job_number:
      letters: The letter credits for the story.
      notes: Additional notes about the story.
      page_count: The page count of the story.
      pencils: The pencil credits for the story.
      script: The script credits for the story.
      sequence_number: The order of the story in the larger issue.
      synopsis: The synopsis of the story.
      title: The title of the story.
      type: The type of the story.
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
    page_count: Optional[Decimal]
    pencils: str
    script: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    sequence_number: int
    synopsis: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    title: Annotated[Optional[str], BeforeValidator(blank_is_none)]
    type: StoryType


class BasicIssue(BaseModel):
    """Contains fields for all Issues.

    Attributes:
      api_url: Url to the resource in the GCD API.
      descriptor: The descriptor of the issue.
      page_count: The page count of the issue.
      price: The price of the issue.
      publication_date: The publication date of the issue.
      series: Url to the Series of this resource in the GCD API.
      series_name: The name of the series.
      variant_of: The URL of the original issue if this issue is a variant.
    """

    api_url: HttpUrl
    descriptor: str
    page_count: Optional[Decimal]
    price: str
    publication_date: str
    series: HttpUrl
    series_name: str
    variant_of: Optional[HttpUrl]

    @property
    def id(self) -> int:
        """The Issue id, extracted from the `api_url` field."""
        if match := re.search(r"/issue/(\d+)/", str(self.api_url)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.api_url)

    @property
    def series_id(self) -> int:
        """The Series id, extracted from the `series` field."""
        if match := re.search(r"/series/(\d+)/", str(self.series)):
            return int(match.group(1))
        raise ValueError("Unable to get id from url: '%s'", self.series)


class Issue(BasicIssue):
    """Extends BasicIssue to include more details.

    Attributes:
      barcode: The barcode of the issue.
      brand:
      cover: The URL of the issue's cover image.
      editing: The editing credits for the issue.
      indicia_frequency: According to the indicia what is the frequency release of the issue.
      indicia_publisher: According to the indicia what is the publisher of the issue.
      isbn: The ISBN of the issue.
      notes: Additional notes about the issue.
      on_sale_date: The on-sale date of the issue.
      rating: The rating of the issue.
      story_set: A list of stories in the issue.
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
