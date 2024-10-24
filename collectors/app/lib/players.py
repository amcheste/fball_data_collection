import datetime
import json
import time
import urllib
import pika
import psycopg
import requests
import logging

from ..utils import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_players():
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes?limit=1000&active=true"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to get first page of players")
        # TODO exception

    for item in response.json().get("items"):
        tmp = urllib.parse.urlparse(item['$ref'])
        id = int(tmp.path.split("/")[-1])

        stmt = '''
        INSERT INTO players (id, url)
        VALUES (%s, %s);
        '''
        args = (id, item['$ref'])
        try:
            cur, conn = database.connect()
            cur.execute(stmt, args)
            conn.commit()
        except psycopg.errors.UniqueViolation:
            continue

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

                stmt = '''
                        INSERT INTO players (id, url)
                        VALUES (%s, %s);
                        '''
                args = (id, item['$ref'])
                try:
                    cur, conn = database.connect()
                    cur.execute(stmt, args)
                    conn.commit()
                except psycopg.errors.UniqueViolation:
                    continue
            page = page + 1

def collect_players():
    """
    Async collector that pulls player details.
    """
    for i in range(0, 25):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq'))
            # pika.ConnectionParameters(host='localhost')) #TODO env vars
            print("Successfully connected to rabbitmq")
            break
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to rabbitmq, sleeping for 5 seconds...")
            time.sleep(5)

    channel = connection.channel()

    channel.queue_declare(queue='players', durable=True)
    print(' [*] Waiting for messages.')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='players', on_message_callback=players_callback)

    channel.start_consuming()

def players_callback(ch, method, properties, body):
    """
    Collect player details callback function.
    :param ch: RabbitMQ channel.
    :param method: RabbitMQ method details.
    :param properties: Channel properties.
    :param body: Message body.
    """
    print(f" [x] Received {body.decode()}")
    data = json.loads(body)
    task_id = data['task_id']
    url = data['url']
    response = requests.get(url)
    data = response.json()

    # Constants
    FANTASY_POSITIONS = {"1": "QB",
                         "2": "RB",
                         "3": "WR",
                         "4": "TE",
                         "5": "K",
                         "16": "DST"}
    if data['position']['id'] not in FANTASY_POSITIONS:
        stmt = '''
        DELETE FROM players WHERE id = %s;
        '''
        args = (data['id'],)
    else:
        stmt = '''
        UPDATE players SET
        name = %s,
        height = %s,
        weight = %s,
        experience = %s,
        position = %s,
        active = %s,
        status = %s,
        age = %s,
        team = %s
        WHERE id = %s;
        '''

        if 'age' not in data:
            data['age'] = None

        if 'team' not in data:
            data['team'] = None

        if 'height' not in data:
            data['height'] = None

        if 'weight' not in data:
            data['weight'] = None

        args = (
            data['displayName'],
            data['height'],
            data['weight'],
            data['experience']['years'],
            data['position']['id'],
            data['active'],
            data['status']['abbreviation'],
            data['age'],
            get_team_id(data['team']['$ref']),
            data['id']
        )

    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()
    #logger.error(json.dumps(data, indent=4))
    logger.error(data['id'])
    if 'statisticslog' in data:
        logger.error(data['statisticslog']['$ref'])
        get_player_stats(player_id=data['id'], url=data['statisticslog']['$ref'])

    #
    # Update status for this player
    stmt = '''
    UPDATE player_collection SET
    status = %s
    WHERE id = %s;
    '''
    #TODO time created/modified?
    args = ('COMPLETED', data['id'])
    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()

    #
    # If there are no more in progress update task status
    stmt = '''
    SELECT id FROM player_collection WHERE status = 'ACCEPTED' and task_id = %s;
    '''
    cur, conn = database.connect()
    args = (task_id,)
    cur.execute(stmt,args)
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

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done")

# TODO return type
def get_team_id(url: str):
    """
    Extracts the team ID from a url.
    :param url: URL containing a team ID.
    :return: Team ID.
    """
    #http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/teams/20?lang=en&region=us'
    tmp = urllib.parse.urlparse(url)
    tmp = tmp.path.split("/")
    for i in range(len(tmp)):
        if tmp[i] == 'teams':
            return tmp[i+1]

def get_player_stats(player_id:str, url: str):
   # logger.error(f"Calling {url}...")
    response = requests.get(url)
    data = response.json()

    for entry in data['entries']:
        #logger.error(json.dumps(entry, indent=4))
        season_id = get_season_id(entry['season']['$ref'])

        for stats in entry['statistics']:
            if stats['type'] == 'total':
                get_season_stats(player_id, season_id, stats['statistics']['$ref'])

def get_season_id(url: str):
    # http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023?lang=en&region=us
    #logger.error(url)
    tmp = urllib.parse.urlparse(url)
    tmp = tmp.path.split("/")
    for i in range(len(tmp)):
        if tmp[i] == 'seasons':
            return tmp[i+1]

def get_season_stats(player_id: str, season_id: str, url: str):
    logger.info(f"AMC: {season_id} -> {url}")
    response = requests.get(url)
    data = response.json()
    #logger.info(json.dumps(data,indent=4))

    type = data['splits']['type']
    logger.info(f'Type = {type}')
    categories = data['splits']['categories']
    for category in categories:
        name = category['name']
        logger.info(f'\tCategory = {name}')
        stats = category['stats']
        for stat in stats:
            if 'perGameValue' not in stat:
                stat['perGameValue'] = None
                #stat['perGameValue'] = 0
            if 'rank' not in stat:
                stat['rank'] = None
            logger.info(f"player_id={player_id}, type={type}, season_id={season_id}, name={name}")
            logger.info(f"value={stat['value']}")
            logger.info(f"perGameValue={stat['perGameValue']}")
            logger.info(f"rank={stat['rank']}")

            stmt = '''
            INSERT INTO player_stats (
                player_id, 
                season_id, 
                type, 
                category,
                name,
                value,
                perGameValue,
                rank
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);
            '''
            args=(player_id, season_id, type, name, stat['name'], stat['value'], stat['perGameValue'], stat['rank'])
            cur, conn = database.connect()
            cur.execute(stmt, args)
            conn.commit()
#{
#    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/4429202/statisticslog?lang=en&region=us",
#    "entries": [
#        {
#            "season": {
#                "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024?lang=en&region=us"
#            },
#            "statistics": [
#                {
#                    "type": "total",
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/1/athletes/4429202/statistics/0?lang=en&region=us"
#                    }
#                },
#                {
#                    "type": "team",
#                    "team": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/teams/20?lang=en&region=us"
#                    },
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/1/teams/20/athletes/4429202/statistics?lang=en&region=us"
#                    }
#                }
#            ]
#        },
#        {
#            "season": {
#                "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023?lang=en&region=us"
#            },
#            "statistics": [
#                {
#                    "type": "total",
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/4429202/statistics/0?lang=en&region=us"
#                    }
#                },
#                {
#                    "type": "team",
#                    "team": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/teams/20?lang=en&region=us"
#                    },
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/teams/20/athletes/4429202/statistics?lang=en&region=us"
#                    }
#                }
#            ]
#        }
#    ]
#}