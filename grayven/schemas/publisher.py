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
    year_began: Optional[int]
    year_ended: Optional[int]
    year_began_uncertain: bool
    year_ended_uncertain: bool
    year_overall_began: Optional[int]
    year_overall_ended: Optional[int]
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
        match = re.search(r"/publisher/(\d+)/", str(self.api_url))
        if match:
            return int(match.group(1))  # Convert the extracted id to an integer
        return None
