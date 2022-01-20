import pika
from pika.exchange_type import ExchangeType
from propzen.common.service_layer.externalbus import IExternalPublisher, ExternalEvent
from propzen.common.adapters.rabbitmq.connection import Connection


class RabbitExternalPublisher(IExternalPublisher):

    def __init__(self, conn: Connection, servicename: str):
        """
        Parameters
        ----------
        conn : Connection
            RabbitMQ Connection from propzen-common
        servicename: str
            Service name of publishing origin
        """

        self.connection = conn
        self.servicename = servicename

    def publish(self, event: ExternalEvent):
        # TODO: implement retry if failed to publish
        with self.connection.connect() as channel:
            channel.exchange_declare(
                exchange=Connection.exchange,
                exchange_type=ExchangeType.direct,
                durable=True)

            channel.basic_publish(
                exchange=Connection.exchange,
                routing_key=event.routingkey(),
                body=event.to_json(),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
