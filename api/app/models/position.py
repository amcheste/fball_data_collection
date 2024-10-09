from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    """
    Position Object
    :param id: Player position ID (e.g. 1)
    :param name: Position name (e.g. Wide Receiver)
    :param abbreviation: Position abbreviation (e.g. WR)
    """
    id: int
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    url: str
