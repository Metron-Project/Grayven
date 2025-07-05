"""The Issue module.

This module provides the following classes:
- BasicIssue
- Issue
- Story
"""

from __future__ import annotations

__all__ = ["BasicIssue", "Issue", "Story"]

import re
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, HttpUrl

from grayven.schemas import BaseModel


class Story(BaseModel):
    """Contains fields relating to the stories inside an Issue.

    Attributes:
      type: The type of the story.
      title: The title of the story.
      feature:
      sequence_number: The order of the story in the larger issue.
      page_count: The page count of the story.
      script: The script credits for the story.
      pencils: The pencil credits for the story.
      inks: The ink credits for the story.
      colors: The color credits for the story.
      letters: The letter credits for the story.
      editing: The editing credits for the story.
      job_number:
      genre: The genre of the story.
      characters: The characters in the story.
      synopsis: The synopsis of the story.
      notes: Additional notes about the story.
    """

    type: str
    title: Annotated[str, Field(max_length=255)]
    feature: str
    sequence_number: Annotated[int, Field(gt=-2147483648, lt=2147483647)]
    page_count: Optional[Decimal] = None
    script: str
    pencils: str
    inks: str
    colors: str
    letters: str
    editing: str
    job_number: Annotated[str, Field(max_length=25)]
    genre: Annotated[str, Field(max_length=255)]
    characters: str
    synopsis: str
    notes: str


class BasicIssue(BaseModel):
    """Contains fields for all Issues.

    Attributes:
      api_url: Url to the resource in the GCD API.
      series_name: The name of the series.
      descriptor: The descriptor of the issue.
      publication_date: The publication date of the issue.
      price: The price of the issue.
      page_count: The page count of the issue.
      variant_of: The URL of the original issue if this issue is a variant.
      series: Url to the Series of this resource in the GCD API.
    """

    api_url: HttpUrl
    series_name: str
    descriptor: str
    publication_date: Annotated[str, Field(max_length=255)]
    price: Annotated[str, Field(max_length=255)]
    page_count: Optional[Decimal] = None
    variant_of: Optional[HttpUrl] = None
    series: HttpUrl

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
      editing: The editing credits for the issue.
      indicia_publisher: According to the indicia what is the publisher of the issue.
      brand:
      isbn: The ISBN of the issue.
      barcode: The barcode of the issue.
      rating: The rating of the issue.
      on_sale_str: The on-sale date of the issue.
      indicia_frequency: According to the indicia what is the frequency release of the issue.
      notes: Additional notes about the issue.
      story_set: A list of stories in the issue.
      cover: The URL of the issue's cover image.
    """

    editing: str
    indicia_publisher: str
    brand: str
    isbn: Annotated[str, Field(max_length=32)]
    barcode: Annotated[str, Field(max_length=38)]
    rating: Annotated[str, Field(max_length=255)] = ""
    on_sale_str: Annotated[str, Field(alias="on_sale_date", max_length=10)]
    indicia_frequency: Annotated[str, Field(max_length=255)]
    notes: str
    story_set: list[Story]
    cover: HttpUrl

    @property
    def on_sale_date(self) -> date | None:
        """Returns the on-sale date as a date object if possible.

        Attempts to parse the on-sale date string and return it as a date object. If parsing
        fails, returns None.
        """
        try:
            return date.fromisoformat(self.on_sale_str.strip())
        except ValueError:
            return None
