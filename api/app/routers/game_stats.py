from fastapi import APIRouter, status

from app.daos.game_stats import list_all_game_stats, list_game_stats

router = APIRouter(
    prefix="/nfl_data/v1/game_stats",
    tags=["players"],
)

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get list of all game stats",
    tags=["games"]
)
async def get_all_game_stats():
    stats = await list_all_game_stats()

    return stats

@router.get(
    "/{game_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a single game stats",
    tags=["games"]
)
async def get_game_stats(game_id: int):
    stats = await list_game_stats(game_id)

    return stats