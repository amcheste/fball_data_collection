from typing import List
from psycopg.rows import class_row

from app.models import PlayerStat
from app.singleton import db_connection_pool


async def list_all_player_stats() -> List[PlayerStat]:
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(PlayerStat)) as cur:
            await cur.execute("SELECT * FROM player_stats;")
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)

    return rows

async def list_player_stats(player_id: int) -> List[PlayerStat]:
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(PlayerStat)) as cur:
            stmt = '''
                SELECT * FROM player_stats WHERE player_id = %s;
            '''
            args = (player_id,)
            await cur.execute(stmt, args)
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)
    return rows