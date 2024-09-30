import time
import pika
import requests

from app.utils import database

def collect_all_teams():
    pass

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
    print(f" [x] Received {body.decode()}")
    print(" [x] Done")

    response = requests.get(body)
    print(response.json())
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
    # Acknowledge the message

    ch.basic_ack(delivery_tag=method.delivery_tag)