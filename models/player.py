from pydantic import BaseModel
from typing import Optional
from utils.database import connect

class Player(BaseModel):
    id: int
    name: str
    weight: float
    height: float
    experience: int
    active: bool
    status: str
    position: int
    age: Optional[int] = None
    team: Optional[int] = None
    stats_url: Optional[str] = None

    def save(self):
        cur, conn = connect()
        stmt = '''
        INSERT INTO players(id, name, weight, height, experience, active, status, position, age, team)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        args = [self.id, self.name, self.weight, self.height, self.experience, self.active, self.status, self.position, self.age, self.team]

        cur.execute(stmt, args)

        conn.commit()
