import datetime
import json
import time
import urllib
import pika
import psycopg
import requests
import logging

from app.utils import database

from app.lib.players import get_season_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_teams(data: dict):
    logger.info("Starting team discovery")
    year = data['start']

    while year <= data['end']:
        url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/teams/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to get first page of positions")
            # TODO exception

        for item in response.json().get("items"):
            tmp = urllib.parse.urlparse(item['$ref'])
            id = int(tmp.path.split("/")[-1])

            stmt = '''
            INSERT INTO teams (id, url)
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
                response = requests.get(f"{url}?page={page + 1}")
                if response.status_code != 200:
                    print(f"Failed to get page number {page} of positions")  # TODO logger?
                    # TODO: Exception

                for item in response.json().get("items"):
                    tmp = urllib.parse.urlparse(item['$ref'])
                    id = int(tmp.path.split("/")[-1])

                    stmt = '''
                    INSERT INTO teams (id, url)
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
        year = year +1


def collect_teams():
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

    channel.queue_declare(queue='teams', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='teams', on_message_callback=teams_callback)

    channel.start_consuming()

def teams_callback(ch, method, properties, body):
    """
    Callback function for collecting position data.
    :param ch: RabbitMQ channel
    :param method: RabbitMQ method.
    :param properties: Queue properties.
    :param body: Message body.
    """
    data = json.loads(body)
    task_id = data['task_id']
    response = requests.get(data['url'])
    data = response.json()
    cur, conn = database.connect()

    stmt = '''
    UPDATE teams SET
    name = %s,
    abbreviation = %s,
    location = %s
    WHERE id = %s;
    '''
    args = (data['displayName'], data['abbreviation'], data['location'], data['id'])
    cur.execute(stmt, args)

    conn.commit()
    team_id=data['id']
    tmp = requests.get(data['statistics']['$ref'])
    data = tmp.json()
    season_id = get_season_id(data['season']['$ref'])
    categories = data['splits']['categories']
    for category in categories:
        name = category['name']
        stats = category['stats']
        for stat in stats:
            if 'perGameValue' not in stat:
                stat['perGameValue'] = None
                #stat['perGameValue'] = 0
            if 'rank' not in stat:
                stat['rank'] = None

            stmt = '''
            INSERT INTO team_stats(
                team_id,
                season_id,
                category,
                name,
                value,
                perGameValue,
                rank
            )VALUES(%s,%s,%s,%s,%s,%s,%s);
            '''
            args = (team_id,season_id, name,stat['name'],stat['value'],stat['perGameValue'],stat['rank'])
            cur, conn = database.connect()
            cur.execute(stmt, args)
            conn.commit()
    #
    # Update status for this position
    stmt = '''
        UPDATE team_collection SET
        status = %s
        WHERE id = %s;
        '''
    # TODO time created/modified?
    args = ('COMPLETED', team_id)
    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()

    #
    # If there are no more in progress update task status
    stmt = '''
        SELECT id FROM team_collection WHERE status = 'ACCEPTED' and task_id = %s;
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

    #
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)