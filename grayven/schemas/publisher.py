__all__ = ["Publisher"]

import re
from datetime import datetime
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


class Publisher(BaseModel):
    api_url: HttpUrl
    country: str
    modified: datetime
    name: str
    year_began: int
    year_ended: int
    year_began_uncertain: bool
    year_ended_uncertain: bool
    year_overall_began: Optional[bytes]  # TODO: Work out typing
    year_overall_ended: Optional[bytes]  # TODO: Work out typing
    year_overall_began_uncertain: bool
    year_overall_ended_uncertain: bool
    notes: str  # or Blank
    url: str  # or Blank
    brand_count: int
    indicia_publisher_count: int
    series_count: int
    issue_count: int

    @property
    def id(self) -> Optional[int]:
        match = re.search(r"/publisher/(\d+)/", self.api_url)
        if match:
            return int(match.group(1))  # Convert the extracted id to an integer
        return None
