from uuid import UUID
from typing import List
from psycopg.rows import class_row

from app.models import Task
from app.models.step import Step
from app.singleton import db_connection_pool


async def create_task(command: str, data_type: str):
    command = command.upper()
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor() as cur:
            stmt = '''
            INSERT INTO tasks (command, data_type) 
            VALUES (%s, %s)
            RETURNING id, time_created, time_modified;
            '''
            args = (command, data_type)
            await cur.execute(stmt, args)
            row = await cur.fetchone()
            id = row[0]
            time_created = row[1]
            time_modified = row[2]

            await db_conn.commit()

    task = Task(id=id, command=command.upper(), data_type=data_type, time_created=time_created, time_modified=time_modified, status='ACCEPTED')

    return task

async def get_tasks():
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Task)) as cur:
            await cur.execute('SELECT * FROM tasks;')
            result = await cur.fetchall()

            return result

async def query_task(task_id: UUID, count: int = 0) -> Task:
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Task)) as cur:

            await cur.execute(
                '''
                SELECT * 
                FROM tasks
                WHERE id = %s
                LIMIT 1;
                ''',
                (task_id,)
            )

            row = await cur.fetchone()

            await db_conn.commit()

    return row

async def get_open_step_count(task_id: UUID, data_type: str) -> int:
    if data_type == 'positions':
        stmt = '''
        SELECT * FROM position_collection WHERE task_id = %s and status != 'COMPLETED';
        '''
        args = (task_id,)
        async with await db_connection_pool.get_connection() as db_conn:
            async with db_conn.cursor() as cur:
                await cur.execute(stmt, args)
                rows = await cur.fetchall()
                await db_conn.commit()

        if rows is None:
            return 0

        return len(rows)

async def get_step_list(task_id: UUID, data_type: str) -> List[Step]:
    if data_type == 'positions':
        stmt = '''
        SELECT * FROM position_collection WHERE task_id = %s;
        '''
        args = (task_id,)
        async with await db_connection_pool.get_connection() as db_conn:
            async with db_conn.cursor(row_factory=class_row(Step)) as cur:
                await cur.execute(stmt, args)
                rows = await cur.fetchall()
                await db_conn.commit()
        return rows