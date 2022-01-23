import asyncio
import json
import functools
import pika
import requests
from s3i.exception import raise_error_from_response, raise_error_from_s3ib_amqp, S3IBrokerRESTError, S3IBrokerAMQPError
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.connection import ConnectionParameters
from pika import PlainCredentials
from pika.exceptions import UnroutableError
from ml.app_logger import APP_LOGGER
from ml.callback import CallbackManager
import ssl

MSG_EXCHANGE = "demo.direct"
EVENT_EXCHANGE = "eventExchange"
BROKER_HOST = "rabbitmq.s3i.vswf.dev"
BROKER_VIRTUAL_HOST = "s3i"
BROKER_API_URL = "https://broker.s3i.vswf.dev/"


class BrokerREST:
    def __init__(self, token, url=BROKER_API_URL):
        self.__token = token
        self.__url = url
        self.__headers = {
            'Content-Type': 'application/json',
            "Authorization": 'Bearer {}'.format(self.__token)
        }

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    def send(self, endpoint, msg):
        response = requests.post(url=self.__url + endpoint, headers=self.__headers, data=msg)
        raise_error_from_response(response, S3IBrokerRESTError, 201)

    def receive_once(self, endpoint):
        response = requests.get(url=self.__url + endpoint,
                                headers=self.__headers)
        return raise_error_from_response(response, S3IBrokerRESTError, 200)


class Broker:
    _ON_CONNECTION_OPEN = "_on_connection_open"
    _ON_CONNECTION_CLOSED = "_on_connection_closed"
    _ON_CHANNEL_OPEN = "_on_channel_open"
    _ON_CHANNEL_CLOSED = "_on_channel_closed"

    def __init__(self, token, endpoint, callback, loop):
        self.__token = token
        self.__endpoint = endpoint #TODO Event Queue, more queue?
        self.__loop = loop
        self.__callback = callback
        self.__credentials = None
        self.__connection_parameters = None
        self.__connection = None
        self.__channel = None
        self.__consumer_tag = None

        self.__is_consuming = False
        self.__callbacks = CallbackManager()

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def connection(self):
        return self.__connection

    @property
    def channel(self):
        return self.__channel

    def connect(self):
        self.__credentials = PlainCredentials(
            username=" ",
            password=self.__token,
            erase_on_connect=True
        )
        self.__connection_parameters = ConnectionParameters(
            host=BROKER_HOST,
            virtual_host=BROKER_VIRTUAL_HOST,
            credentials=self.__credentials,
            heartbeat=10,
            port=5671,
            ssl_options=pika.SSLOptions(ssl.SSLContext())
        )

        self.__connection = AsyncioConnection(
            parameters=self.__connection_parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
            custom_ioloop=self.__loop
        )

    def on_connection_open(self, _unused_connection):
        APP_LOGGER.info("[S3I]: Connection to Broker built")
        self.__channel = _unused_connection.channel(
            on_open_callback=self.on_channel_open
        )
        self.__callbacks.process(
            self._ON_CONNECTION_OPEN,
            self.__loop
        )

    @staticmethod
    def on_connection_open_error(_unused_connection, err):
        APP_LOGGER.error("[S3I]: Connection to broker failed: {}".format(err))

    def on_connection_closed(self, _unused_connection, reason):
        APP_LOGGER.info("[S3I]: Connection to Broker closed: {}".format(reason))
        if self.__is_consuming:
            self.__until_all_closed_and_reconnect()

    def on_channel_open(self, _unused_channel):
        APP_LOGGER.info("[S3I]: Channel open and start consuming messages")
        _unused_channel.add_on_close_callback(self.on_channel_closed)
        _unused_channel.basic_qos(
            prefetch_count=1
        )
        self.start_consuming()
        self.__callbacks.process(
            self._ON_CHANNEL_OPEN,
            self.__loop
        )

    def add_on_channel_open_callback(self, callback, one_shot, *args, **kwargs):
        self.__callbacks.add(
            self._ON_CHANNEL_OPEN,
            callback,
            one_shot,
            False,
            *args,
            **kwargs
        )

    def add_on_connection_open_callback(self, callback, one_shot, *args, **kwargs):
        self.__callbacks.add(
            self._ON_CONNECTION_OPEN,
            callback,
            one_shot,
            False,
            *args,
            **kwargs
        )

    def start_consuming(self):
        self.__consumer_tag = self.__channel.basic_consume(
            auto_ack=True,
            exclusive=True,
            queue=self.__endpoint,
            on_message_callback=self.__callback
        )
        self.__is_consuming = True

    def stop_consuming(self):
        cb = functools.partial(
            self.on_consumer_cancel_ok, userdata=self.__consumer_tag
        )
        self.__channel.basic_cancel(self.__consumer_tag, cb)
        self.__is_consuming = False

    def on_channel_closed(self, channel, reason):
        APP_LOGGER.info("[S3I]: Channel is closed: {}".format(reason))
        if not self.__connection.is_closed:
            self.__connection.close()

    def on_consumer_cancel_ok(self, _unused_frame, userdata):
        if not self.__is_consuming:
            self.__channel.close()

    def reconnect_token_expired(self, token):
        self.__token = token
        """
        Stop comsuming and invoke the stop function for channel and connection 
        """
        if self.__is_consuming:
            self.stop_consuming()
        """
        Check if the channel and connection are closed 
        """
        self.__until_all_closed_and_reconnect()

    async def __until_connected(self):
        if self.__channel is None or self.__connection is None:
            await asyncio.sleep(0.1)
        else:
            if self.__channel.is_open and self.__connection.is_open:
                return
            else:
                self.__loop.call_later(
                    0.1,
                    self.__until_connected
                )

    def __until_all_closed_and_reconnect(self):
        if not self.__channel.is_closed or not self.__connection.is_closed:
            self.__loop.call_later(
                0.1,
                self.__until_all_closed_and_reconnect
            )
        else:
            APP_LOGGER.info("[S3I]: Reconnect to Broker")
            self.connect()

    def send(self, endpoint, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if self.__channel.is_open:
            try:
                raise_error_from_s3ib_amqp(
                    self.__channel.basic_publish,
                    S3IBrokerAMQPError,
                    MSG_EXCHANGE,
                    endpoint,
                    msg,
                    pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2
                    ))
            except S3IBrokerAMQPError as err:
                APP_LOGGER.error("[S3I]: Sending message failed: {}".format(err))
                return False

            else:
                return True

    def publish_event(self, msg, topic):
        if self.__channel.is_open:
            try:
                raise_error_from_s3ib_amqp(
                    self.__channel.basic_publish,
                    S3IBrokerAMQPError,
                    EVENT_EXCHANGE,
                    topic,
                    msg,
                    pika.BasicProperties(
                        content_type="application/json",
                    ))
            except S3IBrokerAMQPError as err:
                APP_LOGGER.error("[S3I]: Sending event failed: {}".format(err))
                return False

            else:
                return True
