import urllib

import pika
import requests
from psycopg.rows import class_row

from app.models import Team
from app.singleton import db_connection_pool


async def list_teams(db_conn):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams;
            '''
        )
        result = await cur.fetchall()

        rows = []
        for row in result:
            rows.append(row)

    return rows


async def get_empty_team_count(db_conn):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE name IS NULL;
            '''
        )
        result = await cur.fetchall()

        return len(result)

async def init_team(db_conn, id: int):
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        stmt = '''
        INSERT INTO teams (id)
        VALUES (%s);
        '''
        args = (id,)

        await cur.execute(stmt, args)

        await db_conn.commit()

async def discover(db_conn, start, end) -> list[Team]:
    teams = {}
    year = start
    # TODO: Can we check if exists before trying to get / write?
    while year < end:
        url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/teams/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to get first page of positions")
            # TODO exception

        for item in response.json().get("items"):
            tmp = urllib.parse.urlparse(item['$ref'])
            id = int(tmp.path.split("/")[-1])
            async with await db_connection_pool.get_connection() as db_conn:
                await init_team(db_conn, id)
                connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                channel = connection.channel()
                channel.queue_declare(queue='teams', durable=True)
                channel.basic_publish(exchange='',
                                      routing_key='teams',
                                      body=item['$ref']
                )

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
                    await init_team(db_conn, id)
                    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                    channel = connection.channel()
                    channel.queue_declare(queue='teams', durable=True)
                    channel.basic_publish(exchange='',
                                          routing_key='teams',
                                          body=item['$ref']
                                          )
            page = page + 1

        year = year + 1

    return teams

async def get_team(db_conn, id: int) -> Team:
    async with db_conn.cursor(row_factory=class_row(Team)) as cur:
        await cur.execute(
            '''
            SELECT * FROM teams WHERE id = %s;
            ''',
            (id,)
        )
        result = await cur.fetchone()

        return result