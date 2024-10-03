from typing import List
from psycopg.rows import class_row

from app.models import Team

async def list_teams(db_conn) -> List[Team]:
    """
    Returns the list of NFL teams stored in the database.
    :param db_conn: Database connection.
    :return: List of NFL team objects.
    """
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

async def get_pending_team_count(db_conn)-> int:
    """
    Returns the number of teams we are currently collecting data on.
    :param db_conn: Database connection.
    :return: Number of pending NFL teams.
    """
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_team(db_conn, id: int):
    """
    Creates an initial NFL team database record.
    :param db_conn: Database connection.
    :param id: NFL team ID.
    """
    async with db_conn.cursor() as cur:
        stmt = '''
        INSERT INTO teams (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()

async def get_team(db_conn, id: int) -> Team:
    """
    Returns details on an NFL team.
    :param db_conn: Database connection.
    :param id: NFL team ID.
    :return: NFL team object.
    """
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result