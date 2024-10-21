from fastapi import APIRouter, status

from app.daos.player_stats import list_all_player_stats, list_player_stats

router = APIRouter(
    prefix="/nfl_data/v1/player_stats",
    tags=["players"],
)

@router.get(
    "/",
    #response_model=List[PlayerStat],
    status_code=status.HTTP_200_OK,
    summary="Get list of all player stats",
    tags=["players"]
)
async def get_all_player_stats():
    stats = await list_all_player_stats()

    return stats

@router.get(
    "/{player_id}",
    #response_model=List[PlayerStat],
    status_code=status.HTTP_200_OK,
    summary="Get a player stats",
    tags=["players"]
)
async def get_player_stats(player_id: int):
    stats = await list_player_stats(player_id)

    return stats