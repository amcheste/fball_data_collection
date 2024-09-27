from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    id: int
    name: Optional[str] = None
    abbreviation: Optional[str] = None
