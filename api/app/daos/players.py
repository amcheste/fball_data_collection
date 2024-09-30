import urllib

import pika
import requests
from psycopg.rows import class_row

from app.models import Player
from app.singleton import db_connection_pool

async def list_players(db_conn):
    async with db_conn.cursor(row_factory=class_row(Player)) as cur:
        await cur.execute(
            '''
            SELECT * FROM players;
            '''
        )
        result = await cur.fetchall()

        rows = []
        for row in result:
            rows.append(row)

    return rows


async def get_pending_player_count(db_conn):
    async with db_conn.cursor(row_factory=class_row(Player)) as cur:
        await cur.execute(
            '''
            SELECT * FROM players WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_player(db_conn, id: int):
    async with db_conn.cursor() as cur:
        stmt = '''
        INSERT INTO players (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()



async def get_player(db_conn, id: int) -> Player:
    async with db_conn.cursor(row_factory=class_row(Player)) as cur:
        await cur.execute(
            '''
            SELECT * FROM players WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result