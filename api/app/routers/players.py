import requests
from fastapi import APIRouter, status, HTTPException
import urllib.parse
import pika
from typing import List

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
async def get_positions():
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
async def get_pending_players():
    count = 0
    async with await db_connection_pool.get_connection() as db_conn:
        count = await get_pending_player_count(db_conn)

    return count

@router.post(
    "/",
    summary="Discover NFL player",
    status_code=status.HTTP_201_CREATED,
    tags=['players']
)
async def discover_players():
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes?limit=1000&active=true"
    count = 0
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to get first page of players")
        # TODO exception
    for item in response.json().get("items"):
        tmp = urllib.parse.urlparse(item['$ref'])
        id = int(tmp.path.split("/")[-1])
        async with await db_connection_pool.get_connection() as db_conn:
            player = await get_player(db_conn, id)
            if player is not None:
                continue
            await init_player(db_conn, id)
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='players', durable=True)
            channel.basic_publish(exchange='',
                              routing_key='players',
                              body=item['$ref']
            )
        count = count + 1

    page_count = response.json().get("pageCount")
    page = response.json().get("pageIndex")
    while page < page_count:
        response = requests.get(f"{url}&page={page + 1}")
        if response.status_code != 200:
            print(f"Failed to get page number {page} of positions")  # TODO logger?
            # TODO: Exception

        for item in response.json().get("items"):
            tmp = urllib.parse.urlparse(item['$ref'])
            id = int(tmp.path.split("/")[-1])

            player = await get_player(db_conn, id)

            if player is not None:
                continue

            async with await db_connection_pool.get_connection() as db_conn:
                await init_player(db_conn, id)
                connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                channel = connection.channel()
                channel.queue_declare(queue='players', durable=True)
                channel.basic_publish(exchange='',
                                      routing_key='players',
                                      body=item['$ref']
                )

            count = count + 1

        page = page + 1


    return count

@router.get(
    "/{id}",
    summary="Get details of a specific NFL player",
    status_code=status.HTTP_201_CREATED,
    tags=['players']
)
async def query_player(id: int):
    async with await db_connection_pool.get_connection() as db_conn:
        player = await get_player(db_conn, id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position with id {id} not found",
        )

    return player