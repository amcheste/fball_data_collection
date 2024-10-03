from typing import List
from psycopg.rows import class_row

from app.models import Position

async def list_positions(db_conn) -> List[Position]:
    """
    Returns all player positions stored in the database.
    :param db_conn: Database connection.
    :return: Position object.
    """
    async with db_conn.cursor(row_factory=class_row(Position)) as cur:
        await cur.execute(
            '''
            SELECT * FROM positions;
            '''
        )
        result = await cur.fetchall()

        rows = []
        for row in result:
            rows.append(row)

    return rows

async def get_position(db_conn, id: int) -> Position | None:
    """
    Get details of a specific player position.
    :param db_conn: Database connection.
    :param id: Player Position ID.
    :return: Player Position object.
    """
    async with db_conn.cursor(row_factory=class_row(Position)) as cur:
        await cur.execute(
            '''
            SELECT * FROM positions WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result

async def get_pending_position_count(db_conn) -> int:
    """
    Returns the number of positions that we are currently collecting data for.
    :param db_conn:
    :return: Number of positions pending data collection.
    """
    async with db_conn.cursor(row_factory=class_row(Position)) as cur:
        await cur.execute(
            '''
            SELECT * FROM positions WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_position(db_conn, id: int):
    """
    Creates initial database record for a player position.
    :param db_conn: Database connection.
    :param id: Player Position ID.
    """
    async with db_conn.cursor() as cur:
        stmt = '''
        INSERT INTO positions (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()