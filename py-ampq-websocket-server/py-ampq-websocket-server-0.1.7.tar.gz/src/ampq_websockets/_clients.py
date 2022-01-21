import datetime
import functools
import json
import logging
import pika
import redis
import time

from typing import Optional

from pika.exceptions import ChannelClosed, AMQPConnectionError

from ._settings import (
    RABBIT_SERVER,
    REDIS_SERVER
)

__all__ = ("RabbitClient", "RedisClient")

TIMEOUT = 5
TIMEOUT_MESSAGE = f"sockjs-redis: error connect, wait {TIMEOUT} sec"


def reconnect_wrapper(func):
    @functools.wraps(func)
    def _func(self, *args, **kwargs):
        while True:
            try:
                return func(self, *args, **kwargs)
            except redis.ConnectionError:
                self.logger.info(TIMEOUT_MESSAGE)
                self.connect()
                time.sleep(TIMEOUT)
    return _func


class RedisClient:
    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config and config["REDIS_SERVER"] or REDIS_SERVER
        self.connect_tries = 0
        self.connecting = False
        self.last_reconnect = None
        self.connect()
        self.logger = logging.getLogger(__name__)

    def get_uptime(self):
        if self.last_reconnect is None:
            return
        return (datetime.datetime.now() - self.last_reconnect).seconds

    def connect(self):
        if self.connecting:
            self.logger.info("sockjs-redis: already connected")
            return

        self.connecting = True
        self.connect_tries += 1
        while self.connecting:
            try:
                self.redis = redis.StrictRedis(
                    host=self.config["HOST"],
                    port=self.config["PORT"],
                    db=self.config["DB"],
                    password=self.config["PASSWORD"]
                )
            except redis.ConnectionError:
                self.logger.info(TIMEOUT_MESSAGE)
                time.sleep(TIMEOUT)
            else:
                self.connecting = False
                self.last_reconnect = datetime.datetime.now()

    def get_real_key(self, key: str) -> str:
        return self.config["PREFIX"] + key

    def log(self, *args) -> None:
        formatters = "%s " * len(args)
        format_string = f"sockjs-redis: {formatters}"
        self.logger.debug(format_string % args)

    @reconnect_wrapper
    def lpush(self, key: str, *args, **kwargs):
        self.log('lpush', key, args, kwargs)
        return self.redis.lpush(self.get_real_key(key), *args, **kwargs)

    @reconnect_wrapper
    def lrange(self, key: str, *args, **kwargs):
        self.log('lrange', key, args, kwargs)
        return self.redis.lrange(self.get_real_key(key), *args, **kwargs)

    @reconnect_wrapper
    def lrem(self, key: str, num: int, value: int):
        self.log('lrem', key, num, value)
        return self.redis.lrem(self.get_real_key(key), num, value)


class RabbitClient:
    def __init__(self, config: Optional[dict] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config and config["RABBIT_SERVER"] or RABBIT_SERVER
        self.connected = False
        self.exchange_name = self.config["EXCHANGE_NAME"]
        self.retry_count = 0

    def _connect(self, on_channel_open, is_retry: bool = False) -> None:
        credentials = pika.PlainCredentials(
            self.config["USER"],
            self.config["PASSWORD"]
        )
        params = pika.ConnectionParameters(
            host=self.config["SERVER"]["HOST"],
            port=self.config["SERVER"]["PORT"],
            virtual_host=self.config["SERVER"]["VHOST"],
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=self.config["EXCHANGE_TYPE"]
        )

        self.connected = True
        if is_retry is False:
            self.retry_count = 0

    def connect(self, is_retry: bool = False) -> None:
        if self.connected is False:
            self._connect(is_retry)

    def _disconnect(self) -> None:
        self.connected = False
        self.connection.disconnect()

    def disconnect(self) -> None:
        if self.connected is True:
            self._disconnect()

    def publish_message(self, message: str, is_retry: bool = False) -> None:
        try:
            self.connect(is_retry)
            self.logger.debug(f"PUBLISH: {message}")

            routing_key = message['host']
            self.channel.basic_publish(
                self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(message)
            )
        except (ChannelClosed, AMQPConnectionError):
            self.disconnect()

            if self.retry_count < 4:
                self.retry_count += 1
                # wait 100 ms
                time.sleep(100 / 1000000.0)
                self.publish_message(message, True)

    def publish_message_simply(self, message: str) -> None:
        room = message.pop('channel')
        connections = self.get_connections(room)
        for conn in connections:
            submessage = message.copy()
            submessage['host'] = conn['host']
            submessage['uid'] = conn['id']
            submessage['room'] = room
            self.channel.basic_publish(
                self.exchange_name,
                routing_key=submessage['host'],
                body=json.dumps(submessage)
            )

    def get_connections(self, room: str):
        self.connect()
        connections = self.redis.lrange(room, 0, -1)
        return [json.loads(_) for _ in connections]
