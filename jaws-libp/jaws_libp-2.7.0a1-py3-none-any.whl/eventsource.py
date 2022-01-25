"""
   Event Sourcing database abstraction layer for Apache Kafka.

   See Also:
       - `Storing Data in Kafka <https://www.confluent.io/blog/okay-store-data-apache-kafka/>`_
       - `Fowler on Event Sourcing <https://martinfowler.com/eaaDev/EventSourcing.html>`_
"""
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Callable
from confluent_kafka import DeserializingConsumer, OFFSET_BEGINNING, Message
from threading import Timer, Event

logger = logging.getLogger(__name__)


class EventSourceListener(ABC):
    """
        Listener interface for EventSourcing callbacks.
    """
    @abstractmethod
    def on_highwater(self) -> None:
        """
            Callback for notification of highwater reached.
        """
        pass

    @abstractmethod
    def on_highwater_timeout(self) -> None:
        """
            Callback notification of timeout before highwater could be reached.
        """
        pass

    @abstractmethod
    def on_batch(self, msgs: Dict[Any, Message]) -> None:
        """
            Callback notification of a batch of messages received.

            :param msgs: Batch of one or more messages, keyed by topic key object
        """
        pass


def log_exception(e: Exception) -> None:
    """
        Simple default action of logging an exception.

        :param e: The Exception
    """
    logger.exception(e)


class TimeoutException(Exception):
    """
        Thrown on asynchronous task timeout
    """
    pass


class EventSourceTable:
    """
        This class provides an Event Source Table abstraction.
    """

    __slots__ = [
        '_config',
        '_consumer',
        '_listeners',
        '_end_reached',
        '_executor',
        '_high',
        '_highwater_signal',
        'is_highwater_timeout',
        '_low',
        '_run',
        '_state'
    ]

    def __init__(self, config: Dict[str, Any]) -> None:
        """
            Create an EventSourceTable instance.

         Args:
             config (dict): Configuration

         Note:
             The configuration options include:

            +-------------------------+---------------------+-----------------------------------------------------+
            | Property Name           | Type                | Description                                         |
            +=========================+=====================+=====================================================+
            | ``bootstrap.servers``   | str                 | Comma-separated list of brokers.                    |
            +-------------------------+---------------------+-----------------------------------------------------+
            |                         |                     | Client group id string.                             |
            | ``group.id``            | str                 | All clients sharing the same group.id belong to the |
            |                         |                     | same group.                                         |
            +-------------------------+---------------------+-----------------------------------------------------+
            |                         |                     | Callable(SerializationContext, bytes) -> obj        |
            | ``key.deserializer``    | callable            |                                                     |
            |                         |                     | Deserializer used for message keys.                 |
            +-------------------------+---------------------+-----------------------------------------------------+
            |                         |                     | Callable(SerializationContext, bytes) -> obj        |
            | ``value.deserializer``  | callable            |                                                     |
            |                         |                     | Deserializer used for message values.               |
            +-------------------------+---------------------+-----------------------------------------------------+
            |                         |                     | Kafka topic name to consume messages from           |
            | ``topic``               | str                 |                                                     |
            |                         |                     |                                                     |
            +-------------------------+---------------------+-----------------------------------------------------+

        Warning:
                Keys must be hashable so your key deserializer generally must generate immutable types.

         """
        self._config: Dict[str, Any] = config
        self._consumer: DeserializingConsumer = None
        self._listeners: List[EventSourceListener] = []
        self._end_reached: bool = False
        self._executor: ThreadPoolExecutor = None
        self._high: int = None
        self._highwater_signal: Event = Event()
        self._is_highwater_timeout: bool = False
        self._low: int = None
        self._run: bool = True
        self._state: Dict[Any, Message] = {}

    def add_listener(self, listener: EventSourceListener) -> None:
        """
            Add a listener.

            :param listener: The EventSourceListener to register
        """

        self._listeners.append(listener)

    def remove_listener(self, listener: EventSourceListener) -> None:
        """
            Remove a listener.

            :param listener: The EventSourceListener to unregister
        """
        self._listeners.remove(listener)

    def await_highwater(self, timeout_seconds: float) -> None:
        """
            Block the calling thread and wait for topic highwater to be reached.

            :param timeout_seconds: Number of seconds to wait before giving up
            :raises TimeoutException: If highwater is not reached before timeout
        """
        logger.debug("await_highwater")
        flag = self._highwater_signal.wait(timeout_seconds)
        if not flag:
            raise TimeoutException

    def start(self, on_exception: Callable[[Exception], None] = log_exception):
        """
            Start monitoring for state updates.

            :param on_exception: function to call if an Exception occurs, defaults to log_exception function
        """
        logger.debug("start")

        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='TableThread')

        future = self._executor.submit(self.__monitor, on_exception)

    def __do_highwater_timeout(self) -> None:
        logger.debug("__do_highwater_timeout")
        self._is_highwater_timeout = True

    def __update_state(self, msg: Message) -> None:
        logger.debug("__update_state")
        if msg.value() is None:
            if msg.key() in self._state:
                del self._state[msg.key()]
        else:
            self._state[msg.key()] = msg

    def __notify_changes(self) -> None:
        for listener in self._listeners:
            listener.on_batch(self._state.copy())

        self._state.clear()

    def __monitor(self, on_exception: Callable[[Exception], None]) -> None:
        try:
            self.__monitor_initial()
            self.__monitor_continue()
        except Exception as e:
            on_exception(e)
        finally:
            self._consumer.close()
            self._executor.shutdown()

    def __monitor_initial(self) -> None:
        logger.debug("__monitor_initial")
        consumer_conf = {'bootstrap.servers': self._config['bootstrap.servers'],
                         'key.deserializer': self._config['key.deserializer'],
                         'value.deserializer': self._config['value.deserializer'],
                         'group.id': self._config['group.id']}

        self._consumer = DeserializingConsumer(consumer_conf)
        self._consumer.subscribe([self._config['topic']], on_assign=self.__on_assign)

        t = Timer(30, self.__do_highwater_timeout)
        t.start()

        while not (self._end_reached or self._is_highwater_timeout):
            msg = self._consumer.poll(1)

            logger.debug("__monitor_initial poll None: {}".format(msg is None))

            msgs = [msg] if msg is not None else None

            if msgs is not None:
                for msg in msgs:
                    self.__update_state(msg)

                    if msg.offset() + 1 == self._high:
                        self._end_reached = True

                self.__notify_changes()

        t.cancel()

        if self._is_highwater_timeout:
            for listener in self._listeners:
                listener.on_highwater_timeout()
        else:
            for listener in self._listeners:
                listener.on_highwater()

    def __monitor_continue(self) -> None:
        logger.debug("__monitor_continue")
        while self._run:
            msg = self._consumer.poll(1)

            logger.debug("__monitor_continue poll None: {}".format(msg is None))

            msgs = [msg] if msg is not None else None

            if msgs is not None:
                for msg in msgs:
                    self.__update_state(msg)

                self.__notify_changes()

    def stop(self) -> None:
        """
            Stop monitoring for state updates.
        """
        logger.debug("stop")
        self._run = False

    def __on_assign(self, consumer, partitions) -> None:

        for p in partitions:
            p.offset = OFFSET_BEGINNING
            self._low, self._high = consumer.get_watermark_offsets(p)

            if self._high == 0:
                self._end_reached = True

        consumer.assign(partitions)

    @property
    def highwater_signal(self) -> Event:
        """
            An Event object for threads to wait on for highwater notification.

            :return: The Event
        """
        return self._highwater_signal


class CachedTable(EventSourceTable):
    """
        Adds an in-memory cache to an EventSourceTable.   Caller should be aware of size of topic being consumed and
        this class should only be used for topics whose data will fit in caller's memory.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self._cache: Dict[Any, Message] = {}

        super().__init__(config)

        self._listener = _CacheListener(self)

        self.add_listener(self._listener)

    def update_cache(self, msgs: Dict[Any, Message]) -> None:
        """
            Merge updated set of unique messages with existing cache, replacing existing keys if any.

            :param msgs: The new messages
        """
        for msg in msgs.values():
            if msg.value() is None:
                if msg.key() in self._cache:
                    del self._cache[msg.key()]
            else:
                self._cache[msg.key()] = msg

    def await_get(self, timeout_seconds) -> Dict[Any, Message]:
        """
            Synchronously get messages up to highwater mark.  Blocks with a timeout.

            :param timeout_seconds: Seconds to wait for highwater to be reached
            :raises TimeoutException: If highwater is not reached before timeout
        """
        self.await_highwater(timeout_seconds)
        return self._cache


class _CacheListener(EventSourceListener):
    """
        Internal listener implementation for the CacheTable
    """

    def __init__(self, parent: CachedTable) -> None:
        """
            Create a new _CacheListener with provided parent.

            :param parent: The parent CachedTable
        """
        self._parent = parent

    def on_highwater(self) -> None:
        self._parent.highwater_signal.set()

    def on_highwater_timeout(self) -> None:
        pass

    def on_batch(self, msgs: Dict[Any, Message]) -> None:
        self._parent.update_cache(msgs)
