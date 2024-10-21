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
            INSERT INTO games (id, year, week, url, pbp_url)
            VALUES (%s, %s, %s, %s, %s);
            '''
            args = (
                event['id'],
                year,
                event['week']['number'],
                f'https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={event["id"]}',
                f'sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{event["id"]}/competitions/{event['id']}/plays?limit=300'
            )
            try:
                cur, conn = database.connect()
                cur.execute(stmt, args)
                conn.commit()
            except psycopg.errors.UniqueViolation:
                continue

        #logger.info(json.dumps(response.json(), indent=4))
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

def collect_games():
    """
    Async data collector that pulls NFL teams off the queue.
    """
    for i in range(0,25):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq'))
                #pika.ConnectionParameters(host='localhost')) #TODO env vars
            print("Successfully connected to rabbitmq")
            break
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to rabbitmq, sleeping for 5 seconds...")
            time.sleep(5)

    channel = connection.channel()

    channel.queue_declare(queue='games', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='games', on_message_callback=games_callback)

    channel.start_consuming()

def games_callback(ch, method, properties, body):
    data = json.loads(body)
    tmp = urllib.parse.urlparse(data['url'])
    game_id = int(tmp.query.split('=')[1])

    #TODO: add play by play support
    #pbp_url = f"https://{data['pbp_url']}"
    task_id = data['task_id']
    response = requests.get(data['url'])
    data = response.json()

    game_info = data['gameInfo']

    teams = {}
    for team in data['boxscore']['teams']:
        #logger.info(json.dumps(team, indent=4))
        if 'name' not in team['team']:
            team['team']['name'] = team['team']['displayName']
        teams[team['homeAway']] = {
            'name': team['team']['name'],
            'abbreviation': team['team']['abbreviation'],
            'team_id': team['team']['id'],
        }
        for stat in team['statistics']:
            stmt = '''
            INSERT INTO game_stats(
                game_id,
                team_id,
                name,
                value
            ) VALUES(%s, %s, %s, %s)
            '''
            args = (game_id, team['team']['id'], stat['name'], stat['displayValue'])
            #logger.error(args)
            cur, conn = database.connect()
            cur.execute(stmt, args)
            conn.commit()

    game_name = f'{teams['away']['name']} v {teams['home']['name']}'
    game_ab = f'{teams['away']['abbreviation']} v {teams['home']['abbreviation']}'

    if 'weather' not in game_info:
        game_info['weather'] = {}

    if 'temperature' not in game_info['weather']:
        game_info['weather']['temperature'] = None
    if 'conditionId' not in game_info['weather']:
        game_info['weather']['conditionId'] = None
    if 'gust' not in game_info['weather']:
        game_info['weather']['gust'] = None
    if 'precipitation' not in game_info['weather']:
        game_info['weather']['precipitation'] = None


    stmt = '''
    UPDATE games SET
    name = %s,
    abbreviation = %s,
    home = %s,
    away = %s,
    location = %s,
    grass = %s,
    temperature = %s,
    condition = %s,
    gust = %s,
    precip = %s
    WHERE id = %s;
    '''
    args = (
        game_name,
        game_ab,
        teams['home']['team_id'],
        teams['away']['team_id'],
        game_info['venue']['address']['city'],
        game_info['venue']['grass'],
        game_info['weather']['temperature'],
        game_info['weather']['conditionId'],
        game_info['weather']['gust'],
        game_info['weather']['precipitation'],
        game_id
    )
    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()


    #
    # Update status for this position
    stmt = '''
        UPDATE game_collection SET
        status = %s
        WHERE id = %s;
        '''
    # TODO time created/modified?
    args = ('COMPLETED', game_id)
    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()

    #
    # If there are no more in progress update task status
    stmt = '''
    SELECT id FROM game_collection WHERE status = 'ACCEPTED' and task_id = %s;
    '''
    cur, conn = database.connect()
    args = (task_id,)
    cur.execute(stmt, args)
    rows = cur.fetchall()
    if len(rows) == 0:
        stmt = '''
            UPDATE tasks SET
            status = %s,
            time_modified = %s
            WHERE id = %s;
            '''
        args = ('COMPLETED', datetime.datetime.now(), task_id)
        cur, conn = database.connect()
        cur.execute(stmt, args)
        conn.commit()

# TODO: Add play by play collection support
#    logger.info(pbp_url)
#    response = requests.get(pbp_url)
#    if response.status_code != 200:
#        pass
#    if response.json()['pageCount'] != 0:
#
#        items = response.json()['items']f
#    else:
#        logger.info("Future game")

    #
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)