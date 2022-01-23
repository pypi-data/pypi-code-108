import asyncio
import functools
import ssl
import requests
import urllib
import json

import pika
import pika.exceptions
from pika.adapters.asyncio_connection import AsyncioConnection
from s3i.exception import raise_error_from_response, raise_error_from_s3ib_amqp, S3IBrokerRESTError, S3IBrokerAMQPError
from s3i.logger import APP_LOGGER
from s3i.callback_manager import CallbackManager

CONTENT_TYPE = "application/json"
HOST = "broker.s3i.vswf.dev"
VIRTUAL_HOST = "s3i"
DIRECT_EXCHANGE = "demo.direct"
EVENT_EXCHANGE = "eventExchange"


class BrokerREST:
    """
    Class Broker REST contains functions to connect to S3I Broker via HTTP REST API, and send and receive messages

    """

    def __init__(self, token, url="https://broker.s3i.vswf.dev/"):
        """
        Constructor

        :param token: Access Token issued from S³I IdentityProvider
        :type token: str
        :param url: url of S³I Broker API
        :type url: str

        """
        self._token = token
        self._url = url
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + self.token}
        self.headers_encrypted = {'Content-Type': 'application/pgp-encrypted',
                                  'Authorization': 'Bearer ' + self.token}

    @property
    def token(self):
        """Returns the JWT currently in use.

        :returns: JWT-Token
        :rtype: str

        """
        return self._token

    @token.setter
    def token(self, new_token):
        """Sets the value of the object's token property to new_token.

        :param new_token: JWT
        :type new_token: str
        """
        self._token = new_token
        self.headers["Authorization"] = "Bearer " + new_token
        self.headers_encrypted["Authorization"] = "Bearer " + new_token

    def send(self, receiver_endpoints, msg, encrypted=False):
        """
        Send a S³I-B message via S³I Broker API
        :param receiver_endpoints: endpoints of the receivers
        :type receiver_endpoints: list of str
        :param msg: message to be sent
        :type msg: str
        :param encrypted: if true, message will be sent encrypted, otherwise not.
        :type encrypted: bool

        """
        end_points_encoded = []
        for receiver_endpoint in receiver_endpoints:
            encoded = urllib.parse.quote(receiver_endpoint, safe="")
            end_points_encoded.append(encoded)

        endpoints = ",".join(end_points_encoded)
        url = "{}{}".format(self._url, endpoints)
        headers = self.headers
        if encrypted:
            headers = self.headers_encrypted
        response = requests.post(url=url, headers=headers, data=msg)
        raise_error_from_response(response, S3IBrokerRESTError, 201)

    def receive_once(self, queue):
        """
        Receive one S3I-B message and do not wait for more messages.

        :param queue: queue which starts a listener in order to receive a single message
        :type queue: str
        :return: received S3I-B message
        :rtype: dict
        """

        queue_encoded = urllib.parse.quote(queue, safe="")
        url = "{}{}".format(self._url, queue_encoded)
        response = requests.get(url=url, headers=self.headers)
        response_json = raise_error_from_response(response, S3IBrokerRESTError, 200)
        return response_json


class BrokerAMQP:
    _ON_CONNECTION_OPEN = "_on_connection_open"
    _ON_CONNECTION_CLOSED = "_on_connection_closed"
    _ON_CHANNEL_OPEN = "_on_channel_open"
    _ON_CHANNEL_CLOSED = "_on_channel_closed"

    def __init__(self, token, endpoint, callback, loop=asyncio.get_event_loop()):
        self.__token = token
        self.__endpoint = endpoint  # TODO Event Queue, more queue?
        self.__loop = loop
        self.__callback = callback
        self.__credentials = None
        self.__connection_parameters = None
        self.__connection = None
        self.__channel = None
        self.__consumer_tag = None

        self.__is_consuming = False
        self.__schedule_messages = []
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
        self.__credentials = pika.PlainCredentials(
            username=" ",
            password=self.__token,
            erase_on_connect=True
        )
        self.__connection_parameters = pika.ConnectionParameters(
            host=HOST,
            virtual_host=VIRTUAL_HOST,
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
        if self.__callback is not None:
            self.start_consuming()
        self.__callbacks.process(
            self._ON_CHANNEL_OPEN,
        )

    def add_on_channel_open_callback(self, callback, one_shot, *args, **kwargs):
        self.__callbacks.add(
            self._ON_CHANNEL_OPEN,
            callback,
            one_shot,
            *args,
            **kwargs
        )

    def add_on_connection_open_callback(self, callback, one_shot, *args, **kwargs):
        self.__callbacks.add(
            self._ON_CONNECTION_OPEN,
            callback,
            one_shot,
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

    def __until_all_closed_and_reconnect(self):
        if not self.__channel.is_closed or not self.__connection.is_closed:
            self.__loop.call_later(
                0.1,
                self.__until_all_closed_and_reconnect
            )
        else:
            APP_LOGGER.info("[S3I]: Reconnect to Broker")
            self.connect()

    def send(self, endpoints, msg):
        try:
            for endpoint in endpoints:
                raise_error_from_s3ib_amqp(
                    self.__channel.basic_publish,
                    S3IBrokerAMQPError,
                    DIRECT_EXCHANGE,
                    endpoint,
                    msg,
                    pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2
                    ))
                APP_LOGGER.info("[S3I]: Sending message successes")

        except S3IBrokerAMQPError as err:
            APP_LOGGER.error("[S3I]: Sending message failed: {}".format(err))

    def publish_event(self, msg, topic):
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

