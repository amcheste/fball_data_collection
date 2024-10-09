#            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
#            channel = connection.channel()
#            channel.queue_declare(queue='positions', durable=True)
#            channel.basic_publish(exchange='',
#                              routing_key='positions',
#                              body=item['$ref']
from typing import Optional

from pika import BlockingConnection
from pydantic import BaseModel

import pika

class Queue(object):

    def __init__(self, name):
        self.__name = name
        self.__channel = None


    def connect(self):
        # TODO: constant
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))

        channel = connection.channel()

        #TODO: Validate queue name

        channel.queue_declare(queue=self.__name, durable=True)

        self.__channel = channel


    def publish(self, data: str):
        self.__channel.basic_publish(
            exchange='',
            routing_key=self.__name,
            body=data,
        )

