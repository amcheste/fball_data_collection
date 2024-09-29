from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int                             # "id": "20"
    name: Optional[str] = None          # "displayName": "New York Jets"
    location: Optional[str] = None      # "location": "New York"
    abbreviation: Optional[str] = None  # "abbreviation": "NYJ"


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