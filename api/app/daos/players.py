from typing import List
from psycopg.rows import class_row

from app.models import Player

async def list_players(db_conn) -> List[Player]:
    """
    Returns a list of all players from the database.
    :param db_conn: Database connection.
    :return: List of Player objects.
    """
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


async def get_pending_player_count(db_conn) -> int:
    """
    Returns the number of players currently being collected
    :param db_conn: Database connection.
    :return: The number of players being collected.
    """
    async with db_conn.cursor(row_factory=class_row(Player)) as cur:
        await cur.execute(
            '''
            SELECT * FROM players WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_player(db_conn, id: int):
    """
    Add initial player entry in the database.
    :param db_conn: Database connection.
    :param id: Player ID
    """
    async with db_conn.cursor() as cur:
        stmt = '''
        INSERT INTO players (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()

async def get_player(db_conn, id: int) -> Player | None:
    """
    Gets player details stored in the database.
    :param db_conn: Database connection.
    :param id: Player ID
    :return: Player object
    """
    async with db_conn.cursor(row_factory=class_row(Player)) as cur:
        await cur.execute(
            '''
            SELECT * FROM players WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result