from pydantic import BaseModel
from typing import Optional

class Player(BaseModel):
    id: int
    name: Optional[str]
    weight: Optional[float]
    height: Optional[float]
    experience: Optional[int]
    active: Optional[bool]
    status: Optional[str]
    position: Optional[int]
    age: Optional[int] = None
    team: Optional[int] = None
    stats_log: Optional[str] = None #???