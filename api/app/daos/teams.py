import urllib

import pika
import requests
from psycopg.rows import class_row

from app.models import Team
from app.singleton import db_connection_pool


async def list_teams(db_conn):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams;
            '''
        )
        result = await cur.fetchall()

        rows = []
        for row in result:
            rows.append(row)

    return rows


async def get_empty_team_count(db_conn):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_team(db_conn, id: int):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        stmt = '''
        INSERT INTO teams (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()

async def get_team(db_conn, id: int) -> Team:
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result