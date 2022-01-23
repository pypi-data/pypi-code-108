#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-09-29 00:59:38
'''
import asyncio
import logging
import os
import pickle
from functools import partial

import aio_pika
import pika

from .decorator import aioretry, retry

logging.getLogger('pika').setLevel(logging.ERROR)

__all__ = ['Pika', 'AioPika']


class Pika:

    def __init__(self, queue='test', **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'user', 'pwd', 'vhost']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 5672)
            user = kwargs.pop('user', 'guest')
            pwd = kwargs.pop('pwd', 'guest')
            vhost = kwargs.pop('vhost', '/')
            self.uri = f'amqp://{user}:{pwd}@{host}:{port}{vhost}'
        elif kwargs.get('uri'):
            self.uri = kwargs.pop('uri')
        elif os.environ.get('MQ_URI'):
            self.uri = os.environ['MQ_URI']
        else:
            host = os.environ.get('MQ_HOST', 'localhost')
            port = os.environ.get('MQ_PORT', 5672)
            user = os.environ.get('MQ_USER', 'guest')
            pwd = os.environ.get('MQ_PWD', 'guest')
            vhost = os.environ.get('MQ_VHOST', '/')
            self.uri = f'amqp://{user}:{pwd}@{host}:{port}{vhost}'

        self.logger = logging.getLogger()
        self.queue = queue
        self._connection = None
        self._channels = {}
        self._queues = {}

    def connect(self):
        if self._connection is None or self._connection.is_closed:
            parameter = pika.URLParameters(self.uri)
            self._connection = pika.BlockingConnection(parameter)
            self.logger.info(self._connection)

    def init(self, queue=None, auto_ack=False):
        queue = queue or self.queue
        self.connect()

        if not (queue in self._channels and not self._channels[queue].is_closed):
            channel = self._connection.channel()
            channel.basic_qos(prefetch_count=1)
            q = channel.queue_declare(queue=queue, auto_delete=False, durable=False)
            self._channels[queue] = channel
            self._queues[queue] = q

        return queue

    def size(self, queue=None):
        queue = self.init(queue)
        return self._queues[queue].method.message_count

    def _consume(self, process, auto_ack, channel, method_frame, header_frame, body):
        try:
            if auto_ack:
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            process(pickle.loads(body))
        except Exception as e:
            self.logger.exception(e)
        finally:
            if not auto_ack:
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def consume(self, process, queue=None, auto_ack=False):
        queue = self.init(queue, auto_ack)
        channel = self._channels[queue]
        channel.basic_consume(queue, partial(self._consume, process, auto_ack))
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            self.close()

    @retry
    def get(self, queue=None, auto_ack=True):
        queue = self.init(queue, auto_ack)
        msg = self._channels[queue].basic_get(queue, auto_ack=auto_ack)
        return pickle.loads(msg[-1])

    @retry
    def publish(self, msg, queue=None):
        queue = self.init(queue)
        self._channels[queue].basic_publish(exchange='',
                                            routing_key=queue,
                                            body=pickle.dumps(msg))

    def close(self):
        for channel in self._channels.values():
            if not channel.is_closed:
                channel.close()
        if self._connection is not None and not self._connection.is_closed:
            self._connection.close()


class AioPika(Pika):

    def __init__(self, queue='test', workers=1, **kwargs):
        super().__init__(queue, **kwargs)
        self.workers = workers
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()

    async def connect(self):
        async with self.lock:
            if self._connection is None or self._connection.is_closed:
                self._connection = await aio_pika.connect_robust(self.uri, loop=self.loop)
                self.logger.info(f'initintize {self._connection}')

    async def size(self, queue=None):
        queue = await self.init(queue)
        return self._queues[queue].declaration_result.message_count

    async def init(self, queue=None, auto_ack=False):
        queue = queue or self.queue
        await self.connect()

        if not (queue in self._channels and not self._channels[queue].is_closed):
            channel = await self._connection.channel()
            await channel.set_qos(prefetch_count=1)
            q = await channel.declare_queue(queue, auto_delete=False, durable=False)
            self._channels[queue] = channel
            self._queues[queue] = q

        return queue

    async def _consume(self, process, queue, auto_ack):
        async for msg in queue:
            try:
                if auto_ack:
                    await msg.ack()
                await process(pickle.loads(msg.body))
            except Exception as e:
                self.logger.exception(e)
            finally:
                if not auto_ack:
                    await msg.ack()

    async def consume(self, process, queue=None, auto_ack=False):
        queue = await self.init(queue, auto_ack)
        for _ in range(self.workers):
            self.loop.create_task(self._consume(process, self._queues[queue], auto_ack))

    @aioretry
    async def get(self, queue=None, auto_ack=True):
        queue = await self.init(queue, auto_ack)
        while True:
            msg = await self._queues[queue].get(no_ack=auto_ack, fail=False, timeout=None)
            if msg:
                return pickle.loads(msg.body)
            else:
                await asyncio.sleep(1)

    @aioretry
    async def publish(self, msg, queue=None):
        queue = await self.init(queue)
        return await self._channels[queue].default_exchange.publish(aio_pika.Message(pickle.dumps(msg)),
                                                                    routing_key=queue)

    async def close(self):
        for channel in self._channels.values():
            if not channel.is_closed:
                await channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
