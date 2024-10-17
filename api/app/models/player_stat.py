import uuid

from pydantic import BaseModel
from typing import Optional

class PlayerStat(BaseModel):
    id: uuid.UUID
    player_id: int
    season_id: int
    type: str
    category: str
    name: str
    value: float
    perGameValue: Optional[float] = None
    rank: Optional[int] = None