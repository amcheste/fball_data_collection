from pydantic import BaseModel
from typing import Optional

class Game(BaseModel):
    id: int
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    week: Optional[int] = None
    year: Optional[int] = None
    home:Optional[str] = None
    away: Optional[str] = None
    url: str
    pbp_url: Optional[str] = None