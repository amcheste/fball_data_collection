from pydantic import BaseModel
from utils.database import connect

class Team(BaseModel):
    id: int                 # "id": "20"
    location: str           # "location": "New York"
    abbreviation: str       # "abbreviation": "NYJ"
    name: str               # "displayName": "New York Jets"

    def save(self):
        cur, conn = connect()
        stmt = '''
        INSERT INTO teams (id, name, abbreviation, location)
        VALUES (%s, %s, %s, %s);
        '''
        args = [self.id, self.name, self.abbreviation, self.location]

        cur.execute(stmt, args)

        conn.commit()

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
