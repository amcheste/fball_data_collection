from fastapi import APIRouter, status, HTTPException

from app.daos.team_stats import list_all_team_stats, list_team_stats

router = APIRouter(
    prefix="/nfl_data/v1/team_stats",
    tags=["teams"],
)

@router.get(
    "/",
    #response_model=List[PlayerStat],
    status_code=status.HTTP_200_OK,
    summary="Get list of all team stats",
    tags=["players"]
)
async def get_all_team_stats():
    stats = await list_all_team_stats()

    return stats

@router.get(
    "/{player_id}",
    #response_model=List[PlayerStat],
    status_code=status.HTTP_200_OK,
    summary="Get a team's stats",
    tags=["teams"]
)
async def get_team_stats(player_id: int):
    stats = await list_team_stats(player_id)

    return stats