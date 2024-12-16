__all__ = ["Genre", "Issue", "Story", "StoryType"]

import re
from enum import Enum
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


class StoryType(str, Enum):
    COVER = "cover"
    COMIC_STORY = "comic story"
    IN_HOUSE_COLUMN = "in-house column"
    ADVERTISEMENT = "advertisement"


class Genre(str, Enum):
    SATIRE_PARODY = "satire-parody"
    SUPERHERO = "superhero"


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
    genre: Optional[Genre]
    characters: str  # or Blank
    synopsis: str
    notes: str  # or Blank


class Issue(BaseModel):
    api_url: HttpUrl
    series_name: str
    descriptor: str
    publication_date: str
    price: str
    page_count: str
    editing: str
    indicia_publisher: str
    brand: str
    isbn: str  # or Blank
    barcode: str  # or Blank
    rating: str  # or Blank
    on_sale_date: str  # or Blank
    indicia_frequency: str
    notes: str
    variant_of: Optional[bytes]  # TODO: Work out typing
    series: HttpUrl
    story_set: list[Story]
    cover: HttpUrl

    @property
    def id(self) -> Optional[int]:
        match = re.search(r"/issue/(\d+)/", self.api_url)
        if match:
            return int(match.group(1))  # Convert the extracted id to an integer
        return None
