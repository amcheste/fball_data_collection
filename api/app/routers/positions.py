import json
import requests
from fastapi import APIRouter, status, HTTPException
from typing import List

from app.daos.tasks import create_task
from app.models.queue import Queue
from app.models import Task
from app.models.position import Position
from app.singleton import db_connection_pool
from app.daos.positions import list_positions, init_position, get_pending_position_count, get_position

"""
    Create a router object for position API endpoints
"""
router = APIRouter(
    prefix="/nfl_data/v1/positions",
    tags=["positions"],
)

@router.get(
    "/",
    summary="List of all NFL positions",
    response_model=List[Position],
    status_code=status.HTTP_200_OK,
    tags=['positions']
)
async def get_positions() -> List[Position]:
    """
    REST endpoint that returns the list of NFL positions.
    :return: List of NFL position objects.
    """
    positions = []
    async with await db_connection_pool.get_connection() as db_conn:
        positions = await list_positions(db_conn)

    return positions

@router.get(
    "/pending",
    summary="Get pending NFL positions",
    response_model=int,
    status_code=status.HTTP_200_OK,
    tags=['positions']
)
async def get_pending_positions() -> int:
    """
    REST endpoint that returns the number of NFL positions we are currently collecting data for.
    :return: The number of NFL positions pending data collection.
    """
    count = 0
    async with await db_connection_pool.get_connection() as db_conn:
        count = await get_pending_position_count(db_conn)

    return count

@router.post(
    "/",
    summary="Discover NFL positions",
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    tags=['positions']
)
async def discover_positions() -> Task:
    """
    Create a task for discovering NFL positions.
    :return: Task object
    """
    #
    # Accept task by creating new Task instance stored in the DB.
    task = await create_task('discover', 'positions')

    #
    # Add it to the task processing queue.
    queue = Queue('tasks')
    queue.connect()
    data = {
        'id': f"{task.id}", # This needs to be seralized into a string and not a UUID object
        'command': 'discover',
        'data_type': 'positions'
    }
    queue.publish(json.dumps(data))

    #
    # Return the task object to the user
    return task


@router.get(
    "/{id}",
    summary="Get details of a specific NFL positions",
    response_model=Position,
    status_code=status.HTTP_201_CREATED,
    tags=['positions']
)
async def query_position(id: int) -> Position:
    """
    REST endpoint that returns details on a specific NFL position.
    :param id: NFL position ID.
    :return: NFL position object.
    """
    async with await db_connection_pool.get_connection() as db_conn:
        position = await get_position(db_conn, id)

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position with id {id} not found",
        )

    return position