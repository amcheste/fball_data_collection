import datetime
import json
import time
import urllib
import pika
import requests
import logging

from app.utils import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_positions():
    url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/positions"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to get first page of positions")
        # TODO exception

    for item in response.json().get("items"):
        tmp = urllib.parse.urlparse(item['$ref'])
        id = int(tmp.path.split("/")[-1])

        stmt = '''
            INSERT INTO positions (id, url)
            VALUES (%s, %s);
            '''
        args = (id, item['$ref'])
        cur, conn = database.connect()
        cur.execute(stmt, args)
        conn.commit()

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
                        INSERT INTO positions (id, url)
                        VALUES (%s, %s);
                        '''
            args = (id, item['$ref'])
            cur, conn = database.connect()
            cur.execute(stmt, args)
            conn.commit()

        page = page + 1

def collect_positions():
    """
    Async data collector that pulls NFL positions off the queue.
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

    channel.queue_declare(queue='positions', durable=True)
    print(' [*] Waiting for messages.')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='positions', on_message_callback=positions_callback)

    channel.start_consuming()

def positions_callback(ch, method, properties, body):
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
    if data['leaf']:
        stmt = '''
            UPDATE positions SET
            name = %s,
            abbreviation = %s
            WHERE id = %s;
        '''
        args = (data['displayName'], data['abbreviation'], data['id'])
        cur.execute(stmt, args)
    else:
        stmt = '''
            DELETE FROM positions WHERE id = %s;
        '''
        args = (data['id'],)
        cur.execute(stmt, args)

    conn.commit()

    #
    # Update status for this position
    stmt = '''
    UPDATE position_collection SET
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
    SELECT id FROM position_collection WHERE status = 'ACCEPTED' and task_id = %s;
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

    #
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)