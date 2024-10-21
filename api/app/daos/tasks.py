from uuid import UUID
from typing import List
from psycopg.rows import class_row

from app.models import Task
from app.models.step import Step
from app.singleton import db_connection_pool

async def create_task(command: str, data_type: str):
    """
    Create a new task entry in the tasks database
    :param command: command type (e.g. DISCOVER | COLLECT)
    :param data_type: data type (e.g. positions, teams, players, etc.)
    :return: Task object
    """
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

    task = Task(
        id=id,
        command=command.upper(),
        data_type=data_type,
        time_created=time_created,
        time_modified=time_modified,
        status='ACCEPTED'
    )

    return task

async def get_tasks():
    """
    Returns the list of tasks
    :return: List of task objects
    """
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Task)) as cur:
            await cur.execute('SELECT * FROM tasks;')
            result = await cur.fetchall()

            return result

async def query_task(task_id: UUID) -> Task:
    """
    Returns details on a specific task.
    :param task_id: Task ID (UUID).
    :return: Returns a task object.
    """
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
    """
    Returns the number of open steps of a specific task.
    :param task_id: Task ID (UUID).
    :param data_type: Data type (e.g. positions, teams, players, etc.)
    :return: Number of open steps.
    """
    if data_type == 'positions':
        stmt = '''
        SELECT * FROM position_collection WHERE task_id = %s and status != 'COMPLETED';
        '''
    elif data_type == 'teams':
        stmt = '''
        SELECT * FROM team_collection WHERE task_id = %s and status != 'COMPLETED';
        '''
    elif data_type == 'games':
        stmt = '''
        SELECT * FROM game_collection WHERE task_id = %s and status != 'COMPLETED';
        '''
    elif data_type == 'players':
        stmt = '''
        SELECT * FROM player_collection WHERE task_id = %s and status != 'COMPLETED';
        '''
    else:
        raise ValueError(f'Invalid data type: {data_type}')


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
    """
    Returns the list of steps of a specific task.
    :param task_id: Task ID (UUID).
    :param data_type: Data type (e.g. positions, teams, players, etc.)
    :return: List of steps.
    """
    if data_type == 'positions':
        stmt = '''
        SELECT * FROM position_collection WHERE task_id = %s;
        '''
    elif data_type == 'teams':
        stmt = '''
        SELECT * FROM team_collection WHERE task_id = %s;
        '''
    elif data_type == 'games':
        stmt = '''
        SELECT * FROM game_collection WHERE task_id = %s;
        '''
    elif data_type == 'players':
        stmt = '''
        SELECT * FROM player_collection WHERE task_id = %s;
        '''
    else:
        raise ValueError(f'Invalid data type: {data_type}')

    args = (task_id,)
    async with await db_connection_pool.get_connection() as db_conn:
        async with db_conn.cursor(row_factory=class_row(Step)) as cur:
            await cur.execute(stmt, args)
            rows = await cur.fetchall()
            await db_conn.commit()
    return rows