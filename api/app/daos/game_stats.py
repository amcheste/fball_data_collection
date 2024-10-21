from typing import List
from psycopg.rows import class_row

from app.models import GameStat
from app.singleton import db_connection_pool

async def list_all_game_stats():
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(GameStat)) as cur:
            await cur.execute("SELECT * FROM game_stats;")
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)

    return rows

async def list_game_stats(game_id: int):
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(GameStat)) as cur:
            stmt = '''
                SELECT * FROM game_stats WHERE player_id = %s;
            '''
            args = (game_id,)
            await cur.execute(stmt, args)
            result = await cur.fetchall()
            rows = []
            for row in result:
                rows.append(row)
    return rows