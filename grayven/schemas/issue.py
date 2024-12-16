__all__ = ["BasicIssue", "Issue", "Story", "StoryType"]

import re
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


class StoryType(str, Enum):
    COVER = "cover"
    COMIC_STORY = "comic story"
    IN_HOUSE_COLUMN = "in-house column"
    ADVERTISEMENT = "advertisement"


class Story(BaseModel):
    type: StoryType
    title: str  # or Blank
    feature: str
    sequence_number: int
    page_count: str
    script: str  # or Blank
    pencils: str  # or Blank
    inks: str  # or Blank
    colors: str  # or Blank
    letters: str  # or Blank
    editing: str  # or Blank
    job_number: str  # or Blank
    genre: str  # or Blank
    characters: str  # or Blank
    synopsis: str
    notes: str  # or Blank


class BasicIssue(BaseModel):
    api_url: HttpUrl
    series_name: str
    descriptor: str
    publication_date: str
    price: str
    page_count: str
    variant_of: Optional[HttpUrl]
    series: HttpUrl

    @property
    def id(self) -> Optional[int]:
        match = re.search(r"/issue/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))
        return None


class Issue(BasicIssue):
    editing: str
    indicia_publisher: str
    brand: str
    isbn: str  # or Blank
    barcode: str  # or Blank
    rating: str  # or Blank
    on_sale_date: Optional[date]
    indicia_frequency: str
    notes: str
    story_set: list[Story]
    cover: HttpUrl
