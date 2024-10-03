from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    """
    NFL Team object.

    :param id: NFL Team ID (e.g. 20).
    :param name: NFL Team name (e.g. New York Jets).
    :param location: NFL Team location (e.g. New York).
    :param abbreviation: NFL Team abbreviation (e.g. NYJ).
    """
    id: int
    name: Optional[str] = None
    location: Optional[str] = None
    abbreviation: Optional[str] = None


#
# TODO: Additional data to consider
#
#    active: bool            # "isActive": true
#    all_star: bool         # "isAllStar": false
#    "record": {
#        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/teams/20/record?lang=en&region=us"
#    },
#    "ranks": {
#        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/teams/20/ranks?lang=en&region=us"
#    },
#    "statistics": {
#        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/teams/20/statistics?lang=en&region=us"
#    },
#    "leaders": {
#        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/teams/20/leaders?lang=en&region=us"
#    }