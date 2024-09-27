import requests
from fastapi import APIRouter, status
import urllib.parse
import pika

from app.models.position import Position
from app.singleton import db_connection_pool
from app.daos.positions import list_positions, init_position, get_empty_position_count

from typing import List

"""
    Create a router object for user API endpoints
"""
router = APIRouter(
    prefix="/nfl_data/v1/positions",
    tags=["users"],
)

@router.get(
    "/",
    summary="List of all NFL positions",
    response_model=List[Position],
    status_code=status.HTTP_200_OK,
    tags=['positions']
)
async def get_positions():
    positions = []
    async with await db_connection_pool.get_connection() as db_conn:
        positions = await list_positions(db_conn)

    return positions

@router.get(
    "/empty",
    response_model=int,
    status_code=status.HTTP_200_OK,
    tags=['positions']
)
async def get_empty_positions():
    count = 0
    async with await db_connection_pool.get_connection() as db_conn:
        count = await get_empty_position_count(db_conn)

    return count
@router.post(
    "/",
    summary="Discover NFL positions",
    status_code=status.HTTP_201_CREATED,
    tags=['positions']
)
async def discover_positions():
    url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/positions"
    count = 0
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to get first page of positions")
        # TODO exception
    for item in response.json().get("items"):
        tmp = urllib.parse.urlparse(item['$ref'])
        id = int(tmp.path.split("/")[-1])
        async with await db_connection_pool.get_connection() as db_conn:
            await init_position(db_conn, id)
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='positions', durable=True)
            channel.basic_publish(exchange='',
                              routing_key='positions',
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
                await init_position(db_conn, id)
                connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                channel = connection.channel()
                channel.queue_declare(queue='positions', durable=True)
                channel.basic_publish(exchange='',
                                      routing_key='positions',
                                      body=item['$ref']
                )
            count = count + 1

        page = page + 1


    return count
