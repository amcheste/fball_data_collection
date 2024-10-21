import json
from fastapi import APIRouter, status, HTTPException
from typing import List

from app.daos.tasks import create_task
from app.models.queue import Queue
from app.models import Task
from app.models import YearRange
from app.models.game import Game
from app.daos.games import list_games, get_pending_game_count, get_game

router = APIRouter(
    prefix="/nfl_data/v1/games",
    tags=["games"],
)

@router.get(
    "/",
    summary="List all NFL games",
    #response_model=List[Game],
    status_code=status.HTTP_200_OK,
    tags=["games"]
)
async def get_games():
    games = await list_games()
    return games


@router.get(
    "/pending",
    summary="List all pending games",
    response_model=int,
    status_code=status.HTTP_200_OK,
    tags=["games"]
)
async def get_pending_games() -> int:
    count = 0
    count = await get_pending_game_count()

    return count
@router.post(
    "/",
    summary="Discover NFL games",
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    tags=["games"]
)
async def discover_games(years: YearRange) -> Task:
    #
    # Accept task by creating new Task instance stored in the DB.
    task = await create_task('discover', 'games')

    #
    # Add it to the task processing queue.
    queue = Queue('tasks')
    queue.connect()
    data = {
        'id': f"{task.id}", # This needs to be seralized into a string and not a UUID object
        'command': 'discover',
        'data_type': 'games',
        'start': years.start,
        'end': years.end
    }
    queue.publish(json.dumps(data))

    #
    # Return the task object to the user
    return task

@router.get(
    "/{id}",
    summary="Retrieve a game by ID",
    response_model=Game,
    status_code=status.HTTP_200_OK,
    tags=["games"]
)
async def query_game(id: int) -> Game:
    game = await get_game(id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {id} not found",
        )