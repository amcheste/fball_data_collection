from pydantic import BaseModel
from typing import Optional

class Player(BaseModel):
    """
    NFL Player Object

    :param id: NFL Player ID (e.g. 3134666).
    :param name: NFL Player first and last name (e.g. Brian Allen).
    :param weight: NFL Player weight (e.g. 303.0).
    :param height: NFL Player height (e.g. 74.0).
    :param experience: NFL Player's years of experience (e.g. 6).
    :param active: NFL Player's active status (e.g. True).'
    :param status: NFL Player's current status (e.g. FA).'
    :param position: NFL Player's current position (e.g. 4).'
    :param age: NFL Player's current age (e.g. 28).'
    :param team: NFL Player's team's ID (e.g. 5)
    :param stats_log: URL that contains pointers to all player stats
    :param url: ESPN player url
    """
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
    stats_log: Optional[str] = None
    url: str