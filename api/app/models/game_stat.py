import uuid

from pydantic import BaseModel

class GameStat(BaseModel):
    id: uuid.UUID
    game_id: int
    team_id: int
    name: str
    value: str