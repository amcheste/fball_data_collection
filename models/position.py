
from pydantic import BaseModel
from utils.database import connect
class Position(BaseModel):
    id: int
    name: str
    abbreviation: str

    def save(self):
        cur,conn = connect()
        stmt = '''
            INSERT INTO positions (id, name, abbreviation)
            VALUES(%s, %s, %s)
        '''
        args = (self.id, self.name, self.abbreviation)

        cur.execute(stmt, args)

        conn.commit()



    #{'$ref': 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/positions/219?lang=en&region=us',
     #'id': '219', 'name': 'Back', 'displayName': 'Back', 'abbreviation': 'B', 'leaf': False}