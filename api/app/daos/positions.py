from psycopg.rows import class_row

from app.models import Position

async def list_positions(db_conn):
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

async def get_empty_position_count(db_conn):
    async with db_conn.cursor(row_factory=class_row(Position)) as cur:
        await cur.execute(
            '''
            SELECT * FROM positions WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)


async def init_position(db_conn, id: int):
    async with db_conn.cursor(row_factory=class_row(Position)) as cur:
        stmt = '''
        INSERT INTO positions (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()