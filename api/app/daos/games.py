from typing import List
from psycopg.rows import class_row

from app.models import Game
from app.singleton import db_connection_pool


async def list_games():
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Game)) as cur:
            await cur.execute(
                '''
                SELECT * FROM games;
                '''
            )
            result = await cur.fetchall()

            rows = []
            for row in result:
                rows.append(row)

        return rows

async def get_pending_game_count():
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Game)) as cur:
            await cur.execute(
                '''
                SELECT * FROM games WHERE name IS NULL;
                '''
            )
            result = await cur.fetchall()

            return len(result)

async def get_game(game_id: int):
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Game)) as cur:
            await cur.execute(
                '''
                SELECT * FROM games WHERE id = %s;
                ''',
                (game_id,)
            )
            result = await cur.fetchone()

            return result