import pika

class Queue(object):
    """
    Object used to connect and publish to a RabbitMQ queue
    """
    def __init__(self, name):
        """
        Creates queue object.
        :param name: Name of the queue.
        """
        self.__name = name
        self.__channel = None


    def connect(self):
        """
        Connects to RabbitMQ queue.
        :return: RabbitMQ channel.
        """
        # TODO: constant
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))

        channel = connection.channel()

        #TODO: Validate queue name

        channel.queue_declare(queue=self.__name, durable=True)

        self.__channel = channel


    def publish(self, data: str):
        """"
        Publishes data to the queue.
        :param data: Data to be published.
        """
        self.__channel.basic_publish(
            exchange='',
            routing_key=self.__name,
            body=data,
        )

