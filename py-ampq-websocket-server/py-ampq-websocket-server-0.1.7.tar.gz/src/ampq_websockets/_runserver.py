import asyncio
import datetime
import json
import logging
import pika
import websockets

from collections import defaultdict
from typing import Optional
from pika.adapters.asyncio_connection import AsyncioConnection
from websockets import WebSocketServerProtocol

from ._clients import RedisClient
from ._settings import HOST, PORT, RABBIT_SERVER
from ._token import Token


__all__ = ("start",)
__author__ = 'smirnov.ev'
logging.basicConfig(level=logging.INFO)


class RabbitConsumer:
    def __init__(self):
        """
        Create a new instance of the consumer class.
        """
        self.should_reconnect = False
        self.was_consuming = False
        self.last_reconnect = datetime.datetime.utcnow()
        self.uptime_start = datetime.datetime.utcnow()

        self._config = self.config and self.config["RABBIT_SERVER"] or RABBIT_SERVER
        self._connection = None
        self._connected = False
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

        self.queue = self._config["QUEUE_NAME"]

    def connect(self):
        """
        This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        logging.info("rabbit consumer: Connecting to RabbitMQ")
        credentials = pika.PlainCredentials(
            self._config["USER"],
            self._config["PASSWORD"]
        )
        params = pika.ConnectionParameters(
            host=self._config["SERVER"]["HOST"],
            port=self._config["SERVER"]["PORT"],
            virtual_host=self._config["SERVER"]["VHOST"],
            credentials=credentials
        )
        return AsyncioConnection(
            parameters=params,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    def close_connection(self) -> None:
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            logging.info(
                "rabbit consumer: Connection is closing or already closed")
        else:
            logging.info("rabbit consumer: Closing connection")
            self._connection.close()

    def on_connection_open(self, _unused_connection: pika.SelectConnection) -> None:
        """
        This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        logging.info("rabbit consumer: Connection opened")
        self.open_channel()

    def on_connection_open_error(
        self, _unused_connection: pika.SelectConnection, err: Exception
    ) -> None:
        """
        This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        logging.error(f"rabbit consumer: Connection open failed: {err}")
        self.reconnect()

    def on_connection_closed(
            self, _unused_connection: pika.SelectConnection, reason: Exception
    ) -> None:
        """
        This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning(
                f"rabbit consumer: Connection closed, reconnect necessary: {reason}"
            )
            self.reconnect()

    def reconnect(self) -> None:
        """
        Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self) -> None:
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        logging.info("rabbit consumer: Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel: pika.channel.Channel) -> None:
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        logging.info("rabbit consumer: Channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()

    def setup_exchange(self) -> None:
        """
        Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        """
        logging.info("rabbit consumer: Channel open, Declaring exchange")
        self._channel.exchange_declare(
            exchange=self._config["EXCHANGE_NAME"],
            exchange_type=self._config["EXCHANGE_TYPE"],
            callback=self.on_exchange_declareok
        )

    def on_exchange_declareok(self, _unused_frame) -> None:
        """
        Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        """
        logging.info('Exchange declared')
        self.setup_queue()

    def setup_queue(self) -> None:
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        logging.info('Declaring queue')
        self._channel.queue_declare(
            queue=self._config["QUEUE_NAME"],
            callback=self.on_queue_declareok
        )

    def on_queue_declareok(self, _unused_frame) -> None:
        """
        Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        """
        logging.info(
            'Binding %s to %s with %s',
            self._config["EXCHANGE_NAME"],
            self._config["QUEUE_NAME"],
            None
        )
        self.queue = _unused_frame.method.queue
        self._channel.queue_bind(
            self._config["QUEUE_NAME"],
            self._config["EXCHANGE_NAME"],
            # routing_key=self.ROUTING_KEY,
            callback=self.on_bindok)

    def on_bindok(self, _unused_frame) -> None:
        """
        Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        """
        logging.info("Queue bound")
        self.set_qos()

    def set_qos(self) -> None:
        """
        This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count,
            callback=self.on_basic_qos_ok
        )

    def on_basic_qos_ok(self, _unused_frame) -> None:
        """
        Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        logging.info(f"QOS set to: {self._prefetch_count}")
        self.start_consuming()

    def start_consuming(self) -> None:
        """
        This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        logging.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self._config["QUEUE_NAME"], self.on_rabbitmq_message, auto_ack=True)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self) -> None:
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        logging.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame) -> None:
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        logging.info(
            "Consumer was cancelled remotely, shutting down: %r", method_frame)
        if self._channel:
            self._channel.close()

    def add_on_channel_close_callback(self) -> None:
        """
        This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logging.info("rabbit consumer:  Adding channel close callback")
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(
        self, channel: pika.channel.Channel, reason: Exception()
    ) -> None:
        """
        Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        logging.warning(
            f"rabbit consumer: Channel {channel} was closed: {reason}")
        self.close_connection()

    def stop(self):
        """
        Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        if not self._closing:
            self._closing = True
            logging.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            logging.info('Stopped')


class Server(RabbitConsumer):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config', None)
        super().__init__(*args, **kwargs)
        self.clients = set()
        self.clients_count = 0
        self.connections = dict()
        self.subscribers = defaultdict(set)
        self.redis_client = RedisClient(self.config)

    def run(self) -> None:
        """
        Run the websocket server by connecting to RabbitMQ & Redis and then
        starting the IOLoop to block and allow the SelectConnection to operate
        """
        self.redis_client.connect()
        self._connection = self.connect()

    def on_rabbitmq_message(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
        """Called when we receive a message from RabbitMQ"""
        if not body:
            return

        self.notify_listeners(body)

    def notify_listeners(self, event: bytes) -> None:
        obj = json.loads(event)

        logging.debug(f"websocket-server: send message {obj}")
        ws = self.connections.get(obj['uid'])
        if ws is None:
            self.redis_client.lrem(
                obj['room'],
                0,
                json.dumps({
                    'id': obj['uid'],
                    'host': obj['host']
                })
            )
        else:
            message = json.dumps({'data': obj['data']})
            asyncio.create_task(ws.send(message))

    def add_subscriber(self, room: str, ws: WebSocketServerProtocol) -> None:
        try:
            uid = str(ws.id)
            self.connections.setdefault(uid, ws)
            client = self.connections[uid]
            self.subscribers[uid].add(room)
            logging.debug(
                f"websocket-server: listener {repr(client)} add to room {room}")
        except KeyError:
            pass

    def remove_subscriber(self, uid: str) -> None:
        for room in self.subscribers[uid]:
            self.redis_client.lrem(
                room,
                0,
                json.dumps({'id': str(uid), 'host': str(self.queue)})
            )

        try:
            client = self.connections[uid]
            del self.subscribers[uid]
            del self.connections[uid]
            logging.debug(
                f"websocket-server: listener {repr(client)} del connection {uid}"
            )
        except KeyError:
            pass

        logging.debug(
            f"websocket-server (Subscirbe):Unsubscribe from connection {uid}")

    def get_clients_count(self) -> None:
        return self.clients_count

    def get_subscribe_connection_count(self) -> None:
        return len(self.connections.keys())

    def get_subscribe_connections(self) -> None:
        return self.connections.keys()

    def get_last_reconnect(self) -> None:
        return self.last_reconnect

    def get_uptime(self) -> None:
        return (datetime.datetime.utcnow() - self.uptime_start).seconds

    def add_client(self, ws: WebSocketServerProtocol) -> None:
        self.clients_count += 1
        self.clients.add(ws)
        logging.debug(f"websocket-server: ws {repr(ws)} added")
        logging.info(f"{ws.remote_address}({ws.id}) connected.")

    def remove_client(self, ws: WebSocketServerProtocol) -> None:
        try:
            self.clients_count -= 1
            self.clients.remove(ws)
            logging.debug(f"websocket-server: ws {repr(ws)} removed")
            logging.info(f"{ws.remote_address} disconnected.")
        except KeyError:
            pass

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.add_client(ws)

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.remove_subscriber(str(ws.id))
        self.remove_client(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for m in ws:
            await self.subscribe(ws, m)
            await self.send(m)

    async def send(self, message: str) -> None:
        await asyncio.wait([
            asyncio.create_task(client.send(message)) for client in self.clients
        ])

    async def handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def subscribe(self, ws: WebSocketServerProtocol, message: str) -> None:
        try:
            uid = str(ws.id)
            obj = json.loads(message)
            token = Token()
            self._compat_transform(obj)
            room = obj['data']['room']

            token.get_data(obj['token'], room)

            self.add_subscriber(room, ws)
            logging.debug(
                f"websocket-server (Subscribe): Subscribe to channel {room}")

            self.redis_client.lpush(
                room,
                json.dumps({'host': str(self.queue), 'id': uid})
            )
            self.connections[uid] = ws
        except (KeyError, TypeError):
            pass

    def _compat_transform(self, obj: dict) -> None:
        data = obj['data']
        if 'room' not in data and 'channel' in data:
            data['room'] = data['channel']


def start(custom_config: Optional[dict] = None) -> None:
    logging.info(f'start websocket-server: {HOST}:{PORT}')
    server = Server(config=custom_config)
    server.run()
    start_server = websockets.serve(server.handler, HOST, PORT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == "__main__":
    start()
