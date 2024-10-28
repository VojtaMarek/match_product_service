
import json
from typing import Final

import pika
import os

from db_manager import DatabaseManager
import config
from models import Item, Category
from product import create_product
import logging

# constants
# rabbitmq_host: Final[str] = os.getenv('RABBITMQ_HOST', config.RABBITMQ_URL)
rabbitmq_host: Final[str] = os.getenv('RABBITMQ_HOST', 'localhost')
db = DatabaseManager(os.environ.get('DB_URL') or config.DB_URL)
queue_offer: Final[str] = 'oc_offer'
queue_category: Final[str] = 'oc_category'
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, host, db):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.db = db

    def declare_queue(self, queue, durable=True) -> None:
        self.channel.queue_declare(queue=queue, durable=durable)

    def bind_queue(self, exchange, queue, routing_key) -> None:
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

    def consume(self, queue) -> None:
        self.channel.basic_consume(queue=queue, on_message_callback=self.callback, auto_ack=True)

    # @pysnooper.snoop()
    def callback(self, ch, method, properties, body):
        message = body.decode()
        type = json.loads(message).get('metadata').get('type')
        data = json.loads(message).get('payload')
        print(f" [x] Received {message}")
        try:
            res = None
            if 'offer' in type:
                data = self.db.serialize_data(data, ['id', 'name', 'description', 'category', 'parameters'])
                data_class = Item(**data)
                res = self.db.insert(data_class, 'id')
            elif 'category' in type:
                data = self.db.serialize_data(data, ['name', 'parent_category'])
                data_class = Category(**data)
                res = self.db.insert(data_class, 'name')
            else:
                logger.warning(f" [x] Received unknown type: {type}")
                return

            if res is None:
                logger.debug(f' [x] Not inserted: {data.get("id")}.')
            else:
                logger.debug(f' [x] Inserted: {data.get("id")}.')
                create_product(res.get('id'))  # standard behavior

        except Exception as e:
            print(f"Error: {e}")

    def start_consuming(self) -> None:
        self.channel.start_consuming()

    def stop_consuming(self) -> None:
        self.channel.stop_consuming()
        # Close the connection
        self.connection.close()


def main():
    reciever = Receiver(rabbitmq_host, db)

    reciever.declare_queue(queue_offer)
    reciever.declare_queue(queue_category)

    reciever.bind_queue('amq.topic', queue_offer, 'oc.offer')
    reciever.bind_queue('amq.topic', queue_category, 'oc.category')

    reciever.consume(queue_offer)
    reciever.consume(queue_category)

    print(" [*] Waiting for messages.")
    reciever.start_consuming()

    reciever.stop_consuming()
    print(" [*] Connection closed")


if __name__ == '__main__':
    main()
