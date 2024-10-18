from typing import List
from psycopg.rows import class_row

from app.models import TeamStat
from app.singleton import db_connection_pool

async def list_all_team_stats() -> List[TeamStat]:
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(TeamStat)) as cur:
            await cur.execute("SELECT * FROM team_stats;")
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)

    return rows

async def list_team_stats(team_id: int) -> List[TeamStat]:
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(TeamStat)) as cur:
            stmt = '''
                SELECT * FROM team_stats WHERE player_id = %s;
            '''
            args = (team_id,)
            await cur.execute(stmt, args)
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)
    return rows