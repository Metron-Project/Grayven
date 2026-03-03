__all__ = ["BasicIssue", "Issue"]

import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, HttpUrl
from pydantic.functional_validators import BeforeValidator

from grayven.schemas._base import BaseModel, blank_is_none


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
        first_line:
        characters: The characters in the story.
        synopsis: The synopsis of the story.
        notes: Additional notes about the story.
        keywords:
    """

    type: str
    title: str
    feature: str
    sequence_number: int
    page_count: Annotated[Decimal | None, BeforeValidator(blank_is_none)] = None
    script: str
    pencils: str
    inks: str
    colors: str
    letters: str
    editing: str
    job_number: str
    genre: str
    first_line: str = ""
    characters: str
    synopsis: str
    notes: str
    keywords: str


class BasicIssue(BaseModel):
    """Contains fields for all Issues.

    Attributes:
        api_url: Url to the resource in the GCD API.
        series_name: The name of the series.
        descriptor: The descriptor of the issue.
        publication_str: The publication date of the issue.
        price: The price of the issue.
        page_count: The page count of the issue.
        variant_of: The URL of the original issue if this issue is a variant.
        series: Url to the Series of this resource in the GCD API.
    """

    api_url: HttpUrl
    series_name: str
    descriptor: str
    publication_str: Annotated[str, Field(alias="publication_date")]
    price: str
    page_count: Annotated[Decimal | None, BeforeValidator(blank_is_none)] = None
    variant_of: Annotated[HttpUrl | None, BeforeValidator(blank_is_none)] = None
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

    @property
    def publication_date(self) -> date | None:
        """Returns the publication date as a date object if possible.

        Attempts to parse the publication date string and return it as a date object. If parsing
        fails, returns None.
        """
        try:
            return date.fromisoformat(self.publication_str.strip())
        except ValueError:
            return None


class Issue(BasicIssue):
    """Extends BasicIssue to include more details.

    Attributes:
        number:
        volume:
        variant_name:
        title:
        key_str:
        editing: The editing credits for the issue.
        indicia_publisher: According to the indicia what is the publisher of the issue.
        brand_emblem:
        isbn: The ISBN of the issue.
        barcode: The barcode of the issue.
        rating: The rating of the issue.
        on_sale_str: The on-sale date of the issue.
        indicia_frequency: According to the indicia what is the frequency release of the issue.
        notes: Additional notes about the issue.
        story_set: A list of stories in the issue.
        cover: The URL of the issue's cover image.
    """

    number: str
    volume: str
    variant_name: str
    title: str
    key_str: Annotated[str, Field(alias="key_date")]
    editing: str
    indicia_publisher: str
    brand_emblem: str
    isbn: str
    barcode: str
    rating: str = ""
    on_sale_str: Annotated[str, Field(alias="on_sale_date")]
    indicia_frequency: str
    notes: str
    indicia_printer: str
    keywords: str
    story_set: list[Story]
    cover: Annotated[HttpUrl | None, BeforeValidator(blank_is_none)] = None

    @property
    def key_date(self) -> date | None:
        """Returns the key date as a date object if possible.

        Attempts to parse the key date string and return it as a date object. If parsing
        fails, returns None.
        """
        try:
            return date.fromisoformat(self.key_str.strip())
        except ValueError:
            return None

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
