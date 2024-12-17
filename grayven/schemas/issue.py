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
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


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

    characters: str  # or Blank
    colors: str  # or Blank
    editing: str  # or Blank
    feature: str
    genre: str  # or Blank
    inks: str  # or Blank
    job_number: str  # or Blank
    letters: str  # or Blank
    notes: str  # or Blank
    page_count: str
    pencils: str  # or Blank
    script: str  # or Blank
    sequence_number: int
    synopsis: str
    title: str  # or Blank
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

    barcode: str  # or Blank
    brand: str
    cover: HttpUrl
    editing: str
    indicia_frequency: str
    indicia_publisher: str
    isbn: str  # or Blank
    notes: str
    on_sale_date: Optional[date]
    rating: str  # or Blank
    story_set: list[Story]
