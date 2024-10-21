import datetime
import json
import time
import urllib
import pika
import psycopg
import requests
import logging

from ..utils import database

from .players import get_season_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_games(data: dict):
    logger.info("Starting game discovery")
    year = data['start']

    while year <= data['end']:
        # 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?limit=1000&dates=2021&seasontype=2'
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?limit=1000&dates={year}&seasontype=2"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to get first page of positions")
            # TODO exception

        events = response.json()['events']
        for event in events:
            stmt = '''
            INSERT INTO games (id, url, pbp_url)
            VALUES (%s, %s, %s);
            '''
            args = (
                event['id'],
                f'https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={event["id"]}',
                f'sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{event["id"]}/competitions/{event['id']}/plays?limit=300'
            )
            try:
                cur, conn = database.connect()
                cur.execute(stmt, args)
                conn.commit()
            except psycopg.errors.UniqueViolation:
                continue

           # 'https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=401671707'
        # TODO pages?
        logger.info(json.dumps(response.json(), indent=4))
        page_count = response.json().get("pageCount")
        page = response.json().get("pageIndex")
        if page_count is not None or page is not None:
            while page < page_count:
                logger.error(f'Page # {page}')
                response = requests.get(f"{url}&page={page + 1}")
                if response.status_code != 200:
                    print(f"Failed to get page number {page} of positions")  # TODO logger?
                    # TODO: Exception

                events = response.json()['events']
                for event in events:
                    stmt = '''
                    INSERT INTO games (id, url, pbp_url)
                    VALUES (%s, %s, %s);
                    '''
                    args = (
                        event['id'],
                        f'https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={event["id"]}',
                        f'sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{event["id"]}/competitions/{event['id']}/plays?limit=300'
                    )
                    try:
                        cur, conn = database.connect()
                        cur.execute(stmt, args)
                        conn.commit()
                    except psycopg.errors.UniqueViolation:
                        continue
                page = page + 1
        year = year + 1