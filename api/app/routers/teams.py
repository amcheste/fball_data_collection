import requests
from fastapi import APIRouter, status, HTTPException
import urllib.parse
import pika
from typing import List

from app.models import YearRange
from app.models.team import Team
from app.singleton import db_connection_pool
from app.daos.teams import list_teams, init_team, get_pending_team_count, get_team

"""
    Create a router object for team API endpoints
"""
router = APIRouter(
    prefix="/nfl_data/v1/teams",
    tags=["teams"],
)

@router.get(
    "/",
    summary="List all NFL teams",
    response_model=List[Team],
    status_code=status.HTTP_200_OK,
    tags=["teams"],
)
async def get_teams() -> List[Team]:
    """
    REST endpoint that returns the list of NFL teams.
    :return: List of NFL team objects.
    """
    teams = []
    async with await db_connection_pool.get_connection() as db_conn:
        teams = await list_teams(db_conn)

    return teams

@router.get(
    "/pending",
    summary="List all pending NFL teams",
    response_model=int,
    status_code=status.HTTP_200_OK,
    tags=["teams"],
)
async def list_teams_pending() -> int:
    """
    REST endpoint that returns the list of NFL team pending detail collection.
    :return:
    """
    count = 0
    async with await db_connection_pool.get_connection() as db_conn:
        count = await get_pending_team_count(db_conn)

    return count

@router.post(
    "/",
    summary="Discover NFL team",
    status_code=status.HTTP_200_OK,
    response_model=int,
    tags=["teams"],
)
async def discover_team(years: YearRange) -> int:
    """
    REST endpoint that discovers NFL teams.
    :param years: Year range object.
    :return: Number of new unique NFL teams identified.
    """
    year = years.start
    print(years)
    count = 0

    while year <= years.end:
        url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/teams/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to get first page of positions")
            # TODO exception

        for item in response.json().get("items"):
            tmp = urllib.parse.urlparse(item['$ref'])
            id = int(tmp.path.split("/")[-1])
            async with await db_connection_pool.get_connection() as db_conn:
                position = await get_team(db_conn, id)
                if position is not None:
                    continue

                await init_team(db_conn, id)
                connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                channel = connection.channel()
                channel.queue_declare(queue='teams', durable=True)
                channel.basic_publish(exchange='',
                                      routing_key='teams',
                                      body=item['$ref']
                )
            count = count + 1

        page_count = response.json().get("pageCount")
        page = response.json().get("pageIndex")

        while page < page_count:
            response = requests.get(f"{url}?page={page + 1}")
            if response.status_code != 200:
                print(f"Failed to get page number {page} of positions")  # TODO logger?
                # TODO: Exception

            for item in response.json().get("items"):
                tmp = urllib.parse.urlparse(item['$ref'])
                id = int(tmp.path.split("/")[-1])
                async with await db_connection_pool.get_connection() as db_conn:
                    position = await get_team(db_conn, id)
                    if position is not None:
                        continue

                    await init_team(db_conn, id)
                    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                    channel = connection.channel()
                    channel.queue_declare(queue='teams', durable=True)
                    channel.basic_publish(exchange='',
                                          routing_key='teams',
                                          body=item['$ref']
                    )
                    count = count + 1
            page = page + 1

        year = year + 1

    return count

@router.get(
    "/{id}",
    summary="Get details of a specific NFL team",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
    tags=['teams']
)
async def query_team(id: int):
    """
    REST endpoint that returns the details of a specific NFL team.
    :param id NFL team ID.
    :return: NFL team object.
    """
    async with await db_connection_pool.get_connection() as db_conn:
        team = await get_team(db_conn, id)

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position with id {id} not found",
        )

    return team