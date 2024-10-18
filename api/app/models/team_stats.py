import uuid

from pydantic import BaseModel
from typing import Optional

class TeamStat(BaseModel):
    id: uuid.UUID
    team_id: int
    season_id: int
    category: str
    name: str
    value: float
    perGameValue: Optional[float] = None
    rank: Optional[int] = None