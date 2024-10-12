import json
import time
import datetime
import pika
import logging

from app.lib.positions import discover_positions
from app.lib.teams import discover_teams
from app.utils import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_tasks():
    for i in range(0,25):
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

    channel.queue_declare(queue='tasks', durable=True)
    print(' [*] Waiting for messages.')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='tasks', on_message_callback=task_callback)

    channel.start_consuming()

def task_callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    data = json.loads(body.decode())
    logger.error(data)

    task_id = data['id']
    command = data['command']
    data_type = data['data_type']

    #
    # Place task in the IN_PROGRESS state
    update_status(task_id=task_id, status='IN_PROGRESS')

    if command.lower() == 'discover':
        logger.info(f"Discovering {data_type}")
        discover_handler(data_type, data)
        logger.info(f"Completed {data_type} discovery")

        #
        # Mark task completed
        update_status(task_id=task_id, status='COMPLETED')
    elif command.lower() == 'collect':
        collect_handler(task_id, data_type)
        update_status(task_id=task_id, status='COMPLETED')
        # Keep the top level task as IN_PROGRESS and let the position queue handler manage status
    else:
        pass

    # ACK
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done")


def discover_handler(data_type: str, data: dict):
    if data_type.lower() == 'positions':
        discover_positions()
    elif data_type.lower() == 'teams':
        discover_teams(data)

def collect_handler(task_id: str, data_type: str):

    #
    # Get list of pending items
    stmt = '''
    SELECT id, url FROM positions WHERE name IS NULL;
    '''
    cur, conn = database.connect()
    cur.execute(stmt)
    results = cur.fetchall()

    #
    # Loop through and add to the positions task table and positions queue
    for row in results:
        logger.info(row)
        stmt = '''
        INSERT INTO position_collection(id, task_id, url)
        VALUES(%s, %s, %s);
        '''
        args = (row[0], task_id, row[1])
        cur, conn = database.connect()
        cur.execute(stmt, args)
        conn.commit()
        data = {
            'task_id': task_id,
            'id': row[0],
            'url': row[1],
        }
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='positions', durable=True)
        channel.basic_publish(exchange='',
            routing_key='positions',
            body=json.dumps(data)
        )


def update_status(task_id: str, status: str):
    logger.error(status)
    stmt = '''
    UPDATE tasks SET
    status = %s,
    time_modified = %s
    WHERE id = %s;
    '''
    args = (status, datetime.datetime.now(),  task_id)
    cur, conn = database.connect()
    cur.execute(stmt, args)
    conn.commit()
