#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Asyncio protocol for RabbitMQ streams.

To handle data received from RabbitMQ Streams broker, there is a choice of
using one of the following base classes

- `asyncio.Protocol` - data chunk is received and added to local buffer
- `asyncio.BufferedProtocol` - buffer view is provided, then updated with
  received data

The first approach can be simulated with local buffer::

    > data = b''

The second approach can be simulated with bytearray, which is updated via
memoryview object::

    > buffer = bytearray(1024 ** 2)
    > mv = memoryview(buffer)

Received chunk of data::

    > chunk = b'0' * 256

Performance test::

    > timeit bd = data + chunk; bd[len(chunk):]
    116 ns ± 0.137 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

    > timeit mv[20:20 + len(chunk)] = chunk
    147 ns ± 0.547 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

The first approach is faster. Open question - under which condition the
second approach could be better solution?
"""

from __future__ import annotations

import asyncio
import dataclasses as dtc
import logging
import typing as tp
from collections import defaultdict

from ..amqp import Message
from ..util import Option
from . import codec
from . import const
from .error import ProtocolError
from .offset import Offset, OffsetType
from .types import MessageQueue
from .util import concatv, retry

logger = logging.getLogger(__name__)

Requests: tp.TypeAlias = dict[int, asyncio.Future[tp.Optional[int]]]
PublishedMessages: tp.TypeAlias = dict[int, 'SentMessages']
Subscriptions = dict[int, 'ReceivedMessages']

# based on https://github.com/rabbitmq/rabbitmq-stream-java-client/blob/83468134c43dcbc9dcc2a862b7ad52f48308d1c8/src/main/java/com/rabbitmq/stream/impl/ClientProperties.java#L40
PEER_PROPERTIES = {
    'product': 'RbFly',
    'platform': 'Python',
    'copyright': 'Copyright (C) Artur Wroblewski',
    'information': 'Licensed under GNU Public License version 3 or later,' \
        ' see https://gitlab.com/wrobell/rbfly',
}

DEFAULT_CREDIT = 10

REQUESTS_KEYS = {
    const.RESPONSE_KEY_PEER_PROPERTIES,    # type: ignore
    const.RESPONSE_KEY_SASL_HANDSHAKE,     # type: ignore
    const.RESPONSE_KEY_SASL_AUTHENTICATE,  # type: ignore
    const.RESPONSE_KEY_OPEN,               # type: ignore
    const.RESPONSE_KEY_CLOSE,              # type: ignore
    const.RESPONSE_KEY_QUERY_OFFSET,       # type: ignore
    const.RESPONSE_KEY_UNSUBSCRIBE,        # type: ignore
    const.RESPONSE_KEY_METADATA_QUERY,     # type: ignore
    const.RESPONSE_KEY_DECLARE_PUBLISHER,  # type: ignore
    const.RESPONSE_KEY_DELETE_PUBLISHER,   # type: ignore
    const.RESPONSE_KEY_SUBSCRIBE,          # type: ignore
    const.RESPONSE_KEY_CREATE_STREAM,      # type: ignore
    const.RESPONSE_KEY_QUERY_PUBLISHER_SEQUENCE,  # type: ignore
}

# TODO: check only for 0x06 code, see https://github.com/rabbitmq/rabbitmq-server/issues/3874
is_stream_na = lambda ex: ex.code in (2, 6)

@dtc.dataclass(frozen=True, slots=True)
class SentMessages:
    task: asyncio.Future[int]
    left: int
    right: int

@dtc.dataclass(frozen=True, slots=True)
class ReceivedMessages:
    task: asyncio.Future[None]
    offset: tp.Optional[int]
    queue: MessageQueue
    amqp: bool

class RabbitMQStreamsProtocol(asyncio.Protocol):
    """
    Asyncio protocol for RabbitMQ streams.

    :var transport: Asyncio transport used by the protocol to send and
        receive RabbitMQ streams frames.
    :var decoder: Frame decoder for RabbitMQ Streams protocol.
    """
    transport: Option[asyncio.Transport]

    def __init__(self) -> None:
        """
        Initialize RabbitMQ streams protocol.

        Instance of the protocol class is created on new connection or
        destroyed when the connection is lots. When connection is lost,
        then any partial frame data is lost.

        The identifiers of requests and messages are tracked in data
        structures stored in context variables. These are recovered on
        new protocol instance.
        """
        self.frame_size = const.DEFAULT_FRAME_SIZE
        self.heartbeat = const.DEFAULT_HEARTBEAT

        self.transport = Option[asyncio.Transport]()
        self.decoder = codec.FrameDecoder()
        self.encoder = codec.Encoder(self.frame_size)
        self.credit = DEFAULT_CREDIT

        self._loop = asyncio.get_running_loop()
        self._requests: Requests = {}
        self._published_messages: PublishedMessages = {}
        self._subscriptions: Subscriptions = {}

        self._correlation_id = max(self._requests, default=0)
        self._waiters: dict[int, asyncio.Future[None]] = {}

    @property
    def connected(self) -> bool:
        return not self.transport.empty

    #
    # high level API
    #
    async def connection_handshake(
        self,
        vhost: str,
        username: tp.Optional[str],
        password: tp.Optional[str]
    ) -> None:
        """
        Perform connection handshake with RabbitMQ streams broker.

        :var vhost: RabbitMQ broker virtual host.
        :var username: Username for authentication.
        :var password: Password for authentication.
        """
        username = username if username else ''
        password = username if password else ''
        await self.send_peer_properties()
        await self.send_sasl_handshake()

        # expect tune frame after sasl authentication; avoid sending open
        # request before tune frame is received and sent back or rabbitmq
        # might close the connection
        tune_waiter = self.create_waiter(const.KEY_TUNE)
        await self.send_sasl_authentication(username, password)
        await tune_waiter

        await self.send_open(vhost)
        logger.info('connection handshake performed')

    async def create_stream(self, stream: str) -> tp.Any:
        """
        Create RabbitMQ stream and query stream metadata.

        :param stream: Stream name.
        """
        try:
            await self.send_create_stream(stream)
        except ProtocolError as ex:
            if ex.code == 5:
                logger.info('rabbitmq stream exists: {}'.format(stream))
            else:
                raise
        else:
            logger.info('rabbitmq stream created: {}'.format(stream))

        # always send metadata query for a stream
        return (await self.query_stream_metadata(stream))

    @retry(ProtocolError, predicate=is_stream_na, retry_after=1)
    async def create_publisher(
        self, publisher_id: int, publisher_ref: str, stream: str
    ) -> int:
        """
        Create RabbitMQ Streams publisher and return last message id.

        :param publisher_id: Publisher id.
        :param publisher_ref: Publisher reference string.
        :param stream: RabbitMQ stream name.

        .. seealso::

           - `declare_publisher`
           - `delete_publisher`
           - `query_message_id`
        """
        await self.declare_publisher(publisher_id, publisher_ref, stream)
        msg_id = await self.query_message_id(publisher_ref, stream)
        return msg_id

    async def delete_publisher(self, publisher_id: int) -> tp.Any:
        """
        Delete RabbitMQ Streams publisher.

        :param publisher_id: Publisher id.

        .. seealso::

           - `create_publisher`
           - `declare_publisher`
        """
        data = codec.FMT_PUBLISHER_ID.pack(publisher_id)
        return (await self.send_request(const.KEY_DELETE_PUBLISHER, data))

    @tp.overload
    async def publish(
            self,
            publisher_id: int,
            message_id: int,
            *messages: Message,
            amqp: tp.Literal[True],
        ) -> tp.Any: ...

    @tp.overload
    async def publish(
            self,
            publisher_id: int,
            message_id: int,
            *messages: bytes,
            amqp: tp.Literal[False],
        ) -> tp.Any: ...

    async def publish(
            self,
            publisher_id: int,
            message_id: int,
            *messages: Message | bytes,
            amqp: bool=True
        ) -> tp.Any:
        """
        Publish multiple messages to RabbitMQ stream.

        Note, that this method does not maintain connection to RabbitMQ
        Streams broker. It is publisher's responsibility to maintain
        a connection.

        :param publisher_id: Publisher id associated with target RabbitMQ
            stream.
        :param message_id: Starting message id of published messages.
        :param messages: Collection of messages to publish.
        """
        task = self._loop.create_future()
        pm = SentMessages(task, message_id, message_id + len(messages) - 1)
        self._published_messages[publisher_id] = pm

        frame = self.encoder.encode_publish(publisher_id, message_id, *messages, amqp=amqp)
        self.send_frame(frame)
        return (await task)

    @retry(ProtocolError, predicate=is_stream_na, retry_after=1)
    async def subscribe(
            self,
            stream: str,
            subscription_id: int,
            offset: Offset,
            amqp: bool,
        ) -> tp.Any:
        """
        Subscribe to receive data from the stream.

        :param stream: Stream name.
        :param subscription_id: Subscription id.
        :param offset: RabbitMQ Streams offset specification.

        .. seealso::

           - `unsubscribe`
           - `send_credit`
        """
        sid = subscription_id
        value = tp.cast(
            tp.Optional[int],
            offset.value if offset.type == OffsetType.OFFSET else None
        )

        task = self._loop.create_future()
        data = codec.encode_subscribe(sid, stream, offset, self.credit)
        self._subscriptions[sid] = ReceivedMessages(task, value, MessageQueue(), amqp)
        return (await self.send_request(const.KEY_SUBSCRIBE, data))

    async def read_stream(self, subscription_id: int, amqp: bool) -> MessageQueue:
        """
        Read RabbitMQ stream messages for the subscription id.

        :param subscription_id: Subscription id for RabbitMQ stream.
        """
        rm = self._subscriptions[subscription_id]
        task = rm.task
        queue = rm.queue
        if task.done() and queue:
            return queue
        elif task.done():
            task = self._loop.create_future()
            self._subscriptions[subscription_id] = ReceivedMessages(task, None, queue, amqp)

        await task
        return queue


    async def unsubscribe(self, subscription_id: int) -> tp.Any:
        """
        Unsubscribe from RabbitMQ stream using the subscription id.

        :param subscription_id: Subscription id.

        .. seealso::

           - `subscribe`
           - `send_credit`
        """
        data = codec.FMT_SUBSCRIPTION_ID.pack(subscription_id)
        del self._subscriptions[subscription_id]
        return (await self.send_request(const.KEY_UNSUBSCRIBE, data))

    async def send_close(self) -> tp.Any:
        """
        Send close request to RabbitMQ Streams broker.
        """
        data = codec.encode_close(1, 'OK')
        return (await self.send_request(const.KEY_CLOSE, data))

    #
    # protocol implementation details
    #

    async def send_peer_properties(self) -> tp.Any:
        """
        Send peer properties to RabbitMQ Streams broker.
        """
        data = codec.encode_properties(PEER_PROPERTIES)
        return (await self.send_request(const.KEY_PEER_PROPERTIES, data))

    async def send_sasl_handshake(self) -> tp.Any:
        """
        Send SASL handshake to RabbitMQ Streams broker.
        """
        return (await self.send_request(const.KEY_SASL_HANDSHAKE, b''))

    async def send_sasl_authentication(
            self, username: str, password: str
        ) -> tp.Any:
        """
        Send SASL authentication message to RabbitMQ Streams broker.
        """
        data = codec.sasl_authenticatation_data(username, password)
        return (await self.send_request(const.KEY_SASL_AUTHENTICATE, data))

    async def send_open(self, vhost: str) -> tp.Any:
        """
        Send open request to RabbitMQ Streams broker.

        :param vhost: RabbitMQ virtual host.
        """
        data = codec.encode_string(vhost)
        r = (await self.send_request(const.KEY_OPEN, data))
        return r

    async def send_create_stream(self, stream: str) -> tp.Any:
        """
        Create RabbitMQ stream.

        :param stream: Stream name.
        """
        data = codec.encode_stream(stream)
        return (await self.send_request(const.KEY_CREATE_STREAM, data))

    async def query_stream_metadata(self, stream: str) -> tp.Any:
        """
        Query RabbitMQ stream metadata.

        :param stream: Stream name.
        """
        data = codec.encode_metadata_query(stream)
        return (await self.send_request(const.KEY_METADATA_QUERY, data))

    async def declare_publisher(
        self, publisher_id: int, publisher_ref: str, stream: str
    ) -> tp.Any:
        """
        Declare RabbitMQ Streams publisher.

        :param publisher_id: Publisher id.
        :param publisher_ref: Publisher reference string.
        :param stream: RabbitMQ stream name.

        .. seealso::

           - `create_publisher`
           - `delete_publisher`
        """
        data = codec.declare_publisher(publisher_id, publisher_ref, stream)
        return (await self.send_request(const.KEY_DECLARE_PUBLISHER, data))

    async def query_offset(self, stream: str, reference: str) -> int:
        """
        Query RabbitMQ stream offset value for stream using reference.

        :param stream: Name of RabbitMQ stream.
        :param reference: Reference for RabbitMQ stream offset.
        """
        data = codec.encode_query_offset(stream, reference)
        offset = await self.send_request(const.KEY_QUERY_OFFSET, data)
        return tp.cast(int, offset)

    async def query_message_id(self, publisher_ref: str, stream: str) -> int:
        """
        Query last message id for the publisher and the stream (query
        publisher sequence).

        :param publisher_ref: Publisher reference.
        :param stream: RabbitMQ stream name.
        """
        data = codec.encode_query_message_id(publisher_ref, stream)
        msg_id = await self.send_request(
            const.KEY_QUERY_PUBLISHER_SEQUENCE, data
        )
        return tp.cast(int, msg_id)

    def send_credit(self, subscription_id: int) -> None:
        """
        Update message delivery credit for the subscription.

        Note, that this method is not a coroutine. The credit request is
        sent and no response is expected from RabbitMQ Streams broker.

        :param subscription_id: Subscription id.
        """
        # TODO: can we use more credit and then shutdown cleanly?
        self.credit = 1
        data = codec.encode_credit(subscription_id, 1)
        self.send_frame(data)

    def store_offset(self, stream: str, reference: str, offset: Offset) -> None:
        """
        Store RabbitMQ Streams offset.

        :param stream: Name of RabbitMQ stream.
        :param reference: Reference for RabbitMQ stream offset.
        :param offset: RabbitMQ Streams offset specification.
        """
        data = codec.encode_store_offset(stream, reference, offset)
        self.send_frame(data)

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = Option(tp.cast(asyncio.Transport, transport))

    def connection_lost(self, ex: tp.Optional[Exception]) -> None:
        self.transport = Option[asyncio.Transport]()

        all_tasks = tp.cast(
            tp.Iterable[asyncio.Future[None]],
            concatv(
                self._requests.values(),
                (p.task for p in self._published_messages.values()),
                (r.task for r in self._subscriptions.values()),
            ),
        )
        tasks = (t for t in all_tasks if not t.done())
        for t in tasks:
            t.set_exception(ConnectionError('connection closed'))

        logger.info('connection is closed')

    def abort(self) -> None:
        """
        Close Asyncio transport used by the protocol.
        """
        if not self.transport.empty:
            self.transport.value.abort()

    def data_received(self, chunk: bytes) -> None:
        for start, key in self.decoder.commands(chunk):
            # NOTE: data is updated after FrameDecoder.commands call
            data = self.decoder.data
            if key == const.KEY_PUBLISH_CONFIRM:
                self.process_publish_confirm(data, start)

            elif key == const.KEY_DELIVER:
                self.process_message_delivery(data, start)

            elif key == const.KEY_HEARTBEAT:
                # simply wait for a heartbeat from rabbitmq streams broker
                # and respond with another heartbeat; this seems to work
                # and active heartbeat sending by client seems to be not
                # necessary
                self.send_frame(codec.HEARTBEAT)
                logger.info('heartbeat frame sent')

            elif key == const.KEY_TUNE:
                # decode tune command and accept what rabbitmq streams
                # broker provides
                frame_size, heartbeat = codec.FMT_TUNE.unpack_from(data, start)[-2:]
                self.frame_size = frame_size
                self.heartbeat = heartbeat
                self.encode = codec.Encoder(frame_size)

                # tune request is sent by rabbitmq streams broker; respond
                # to the request with another tune request (not a response)
                self.send_frame(data[start:start + codec.FMT_TUNE.size])
                task = self._waiters.pop(key)
                task.set_result(None)
                logger.info('tune frame sent')

            elif key == const.RESPONSE_KEY_CREDIT:  # type: ignore
                code, subscription_id = codec.decode_credit(data, start)
                logger.warning(
                    'received credit response, code={}, subscription id={}'
                    .format(code, subscription_id)
                )

            elif key == const.KEY_CLOSE:
                code, reason = codec.decode_close(data, start)
                logger.info(
                    'received close request, code={}, reason={}'
                    .format(code, reason)
                )
                self.abort()

            elif key in REQUESTS_KEYS:
                self.process_request_response(key, data, start)

            elif key == const.KEY_PUBLISH_ERROR:
                publisher_id, errors = codec.decode_publish_error(data, start)
                logger.warning(
                    'publish error; publisher={}, publishing id=0x{:x},' \
                    ' error=0x{:04x}, num errors={}'.format(
                        publisher_id, *errors[0], len(errors)
                ))
            else:
                logger.warning('unknown key; key=0x{:04x}'.format(key))

    def send_frame(self, data: bytes) -> None:
        """
        Send RabbitMQ streams frame to broker.
        """
        transport = self.transport.value
        n = len(data)
        if n > self.frame_size:
            raise ProtocolError(0x0e, 'Frame too large')
        transport.write(codec.FMT_FRAME_SIZE.pack(n))
        transport.write(data)

    async def send_request(self, key: int, data: bytes) -> tp.Any:
        self._correlation_id += 1
        correlation_id = self._correlation_id

        request_data = codec.create_request(key, correlation_id, data)
        self.send_frame(request_data)
        task = self._requests[correlation_id] = self._loop.create_future()

        if __debug__:
            logger.debug(
                'request sent, key=0x{:02x}, correlation_id={}'
                .format(key, correlation_id)
            )
        return (await task)

    def create_waiter(self, key: int) -> asyncio.Future[None]:
        """
        Create Asyncio future to wait for specific RabbitMQ Streams
        request.

        :param key: Key of request to wait for.
        """
        assert key not in self._waiters
        task = self._loop.create_future()
        self._waiters[key] = task
        return task

    def process_request_response(self, key: int, data: bytes, start: int) -> None:
        correlation_id, code = codec.decode_request(data, start)
        logger.debug(
            'received request response, key=0x{:04x},'
            ' correlation_id={}, code={}'.format(
                key, correlation_id, code
            )
        )

        task = self._requests.pop(correlation_id)
        if code == 1 and key == const.RESPONSE_KEY_QUERY_PUBLISHER_SEQUENCE:  # type: ignore
            msg_id = codec.FMT_MESSAGE_ID.unpack_from(
                data, start + codec.LEN_HEADER + codec.LEN_REQUEST_RESPONSE
            )
            task.set_result(msg_id[0])
        elif code == 1 and key == const.RESPONSE_KEY_QUERY_OFFSET:  # type: ignore
            offset = codec.FMT_OFFSET_VALUE.unpack_from(
                data, start + codec.LEN_HEADER +  + codec.LEN_REQUEST_RESPONSE
            )
            task.set_result(offset[0])
        elif code == 1 and key == const.RESPONSE_KEY_CLOSE:  # type: ignore
            self.abort()
            task.set_result(None)
        elif code == 1:
            task.set_result(None)
        elif code == 0 and key == const.RESPONSE_KEY_METADATA_QUERY:  # type: ignore
            # NOTE: metadata query response has no code; the value comes
            # from first byte of broker array
            # TODO: populate with metadata response
            task.set_result(None)
        else:
            msg = 'RabbitMQ Stream protocol error: 0x{:02x}'.format(code)
            task.set_exception(ProtocolError(code, msg))

    def process_publish_confirm(self, data: bytes, start: int) -> None:
        """
        Process published message confirmation.

        :param data: Data received from RabbitMQ Streams broker.
        :param start: Data starting point.
        """
        publisher_id, left, right = codec.decode_publish_confirm(
            data, start + codec.LEN_HEADER
        )
        pm = self._published_messages.pop(publisher_id)

        if left == pm.left and right == pm.right:
            pm.task.set_result(0)
        elif left == pm.left:
            self._published_messages[publisher_id] = dtc.replace(
                pm, left=right + 1
            )
        else:
            assert False, 'wrong assumptions about message ids'

    def process_message_delivery(self, data: bytes, start: int) -> None:
        """
        Process message delivery from RabbitMQ Streams broker.

        :param data: Data received from RabbitMQ Streams broker.
        :param start: Data starting point.
        """
        offset = start + codec.LEN_HEADER
        sid = data[offset]
        if sid in self._subscriptions:
            rm = self._subscriptions[sid]
            task = rm.task
            codec.decode_messages(data, offset + 1, rm.offset, rm.queue, rm.amqp)

            self.credit =- 1
            if self.credit <= 0:
                self.send_credit(sid)

            if not task.done():
                task.set_result(None)
        else:
            logger.warning(
                'subscription not found, id={}'.format(sid)
            )

# vim: sw=4:et:ai
