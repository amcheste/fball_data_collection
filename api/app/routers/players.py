import json
from fastapi import APIRouter, status, HTTPException
from typing import List

from app.daos.tasks import create_task
from app.models import Task, Queue
from app.models.player import Player
from app.singleton import db_connection_pool
from app.daos.players import list_players, init_player, get_pending_player_count, get_player

"""
    Create a router object for player API endpoints
"""
router = APIRouter(
    prefix="/nfl_data/v1/players",
    tags=["players"],
)

@router.get(
    "/",
    summary="List of all NFL players",
    response_model=List[Player],
    status_code=status.HTTP_200_OK,
    tags=['players']
)
async def get_players() -> List[Player]:
    """
    REST endpoint that lists all NFL players
    :return: List of NFL players
    """
    players = []
    async with await db_connection_pool.get_connection() as db_conn:
        players = await list_players(db_conn)

    return players

@router.get(
    "/pending",
    summary="Get the number of pending players",
    response_model=int,
    status_code=status.HTTP_200_OK,
    tags=['players']
)
async def get_pending_players() -> int:
    """
    Rest endpoint that returns the number of pending players.
    :return: Number of pending players.
    """
    count = 0
    async with await db_connection_pool.get_connection() as db_conn:
        count = await get_pending_player_count(db_conn)

    return count

@router.post(
    "/",
    summary="Discover NFL player",
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    tags=['players']
)
async def discover_players() -> Task:
    #
    # Accept task by creating new Task instance stored in the DB.
    task = await create_task('discover', 'players')

    #
    # Add it to the task processing queue.
    queue = Queue('tasks')
    queue.connect()
    data = {
        'id': f"{task.id}", # This needs to be seralized into a string and not a UUID object
        'command': 'discover',
        'data_type': 'players',
    }
    queue.publish(json.dumps(data))

    #
    # Return the task object to the user
    return task

@router.get(
    "/{id}",
    summary="Get details of a specific NFL player",
    response_model=Player,
    status_code=status.HTTP_201_CREATED,
    tags=['players']
)
async def query_player(id: int) -> Player:
    """
    REST endpoint that returns details of a specific NFL player.
    :param id: NFL Player ID
    :return: NFL Player object
    """
    async with await db_connection_pool.get_connection() as db_conn:
        player = await get_player(db_conn, id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position with id {id} not found",
        )

    return player