__all__ = ["Series"]

import re
from typing import Optional

from pydantic import HttpUrl

from grayven.schemas import BaseModel


class Series(BaseModel):
    api_url: HttpUrl
    name: str
    country: str
    language: str
    active_issues: list[HttpUrl]
    issue_descriptors: list[str]
    color: str
    dimensions: str
    paper_stock: str
    binding: str
    publishing_format: str
    notes: str  # or Blank
    year_began: int
    year_ended: int
    publisher: HttpUrl

    @property
    def id(self) -> Optional[int]:
        match = re.search(r"/series/(\d+)/", self.api_url)
        if match:
            return int(match.group(1))  # Convert the extracted id to an integer
        return None
