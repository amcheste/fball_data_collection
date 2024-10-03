import time
import pika
import requests

from app.utils import database

def collect_all_positions():
    """
    Async data collector for all NFL positions in the queue.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    response = requests.get('http://guest:guest@localhost:15672/api/queues/%2f/positions')
    messages = response.json()['messages']

    for method_frame, properties, body in channel.consume('positions'):
        response = requests.get(body)
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
        # Acknowledge the message
        channel.basic_ack(method_frame.delivery_tag)

        # Escape out of the loop after 10 messages
        if method_frame.delivery_tag == messages:
            break

    # Cancel the consumer and return any pending messages
    requeued_messages = channel.cancel()
    print('Requeued %i messages' % requeued_messages)

    # Close the channel and the connection
    channel.close()
    connection.close()

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
    print(f" [x] Received {body.decode()}")
    print(" [x] Done")

    response = requests.get(body)
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
    # Acknowledge the message

    ch.basic_ack(delivery_tag=method.delivery_tag)