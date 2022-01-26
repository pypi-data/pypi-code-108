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
        Listener interface for EventSourceTable callbacks.
    """
    @abstractmethod
    def on_highwater(self) -> None:
        """
            Callback for notification of highwater reached.
        """
        pass

    @abstractmethod
    def on_batch(self, msgs: List[Message]) -> None:
        """
            Callback notification of a batch of messages received.

            This method is called regardless of highwater status.

            :param msgs: Batch of one or more ordered messages
        """
        pass


class CacheListener(ABC):
    """
        Listener interface for CachedTable callbacks.
    """

    @abstractmethod
    def on_load(self, cache: Dict[Any, Message]) -> None:
        """
            Callback for notification of initial cache load.
        """
        pass

    @abstractmethod
    def on_update(self, msgs: List[Message]) -> None:
        """
            Callback notification of a batch of update messages.

            This method is only called after highwater has been reached.

            Note: The compacted cache has already been updated by the time this function is called.

            :param msgs: Batch of one or more ordered messages
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
        '_executor',
        '_high',
        '_highwater_reached',
        '_highwater_signal',
        '_is_highwater_timeout',
        '_low',
        '_on_exception',
        '_run',
        '_state'
    ]

    def __init__(self, config: Dict[str, Any], on_exception: Callable[[Exception], None] = log_exception) -> None:
        """
            Create an EventSourceTable instance.

         Args:
             config (dict): Configuration

             on_exception (Callable): Function to call when an asynchronous exception occurs, including a Timeout.


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
            |                         |                     | Number of seconds to wait for highwater             |
            | ``highwater.timeout``   | float               |                                                     |
            |                         |                     |                                                     |
            +-------------------------+---------------------+-----------------------------------------------------+

        Warning:
                Keys must be hashable so your key deserializer generally must generate immutable types.

         """
        self._config: Dict[str, Any] = config
        self._on_exception = on_exception
        self._consumer: DeserializingConsumer = None
        self._listeners: List[EventSourceListener] = []
        self._executor: ThreadPoolExecutor = None
        self._high: int = None
        self._highwater_reached: bool = False
        self._highwater_signal: Event = Event()
        self._is_highwater_timeout: bool = False
        self._low: int = None
        self._run: bool = True
        self._state: List[Message] = []

    def add_listener(self, listener: EventSourceListener) -> None:
        """
            Add an EventSourceListener.

            :param listener: The EventSourceListener to register
        """

        self._listeners.append(listener)

    def remove_listener(self, listener: EventSourceListener) -> None:
        """
            Remove an EventSourceListener.

            :param listener: The EventSourceListener to unregister
        """
        self._listeners.remove(listener)

    def await_highwater(self) -> None:
        """
            Block the calling thread and wait for topic highwater to be reached.

            See: The 'highwater.timeout' option passed to the config Dict in constructor

            :raises TimeoutException: If highwater is not reached before timeout
        """
        logger.debug("await_highwater")
        self._highwater_signal.wait()
        if self._is_highwater_timeout:
            raise TimeoutException()

    def start(self):
        """
            Start monitoring for state updates.

            Note: start() should only be called once.  I'm too lazy to come up with some thread-safe locking check
            to ensure it, so just like Python doesn't actually have private members, I'm not actually going to stop you,
            but you've been warned.
        """
        logger.debug("start")

        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='TableThread')

        future = self._executor.submit(self.__monitor)

    def highwater_reached(self) -> bool:
        """
            Check whether initial highwater has been reached.

            :return: True if highwater reached
        """

        return self._highwater_reached

    def __do_highwater_timeout(self) -> None:
        logger.debug("__do_highwater_timeout")
        self._is_highwater_timeout = True

    def __update_state(self, msg: Message) -> None:
        logger.debug("__update_state")
        self._state.append(msg)

    def __notify_changes(self) -> None:
        for listener in self._listeners:
            listener.on_batch(self._state.copy())

        self._state.clear()

    def __monitor(self) -> None:
        try:
            self.__monitor_initial()
            self.__monitor_continue()
        except Exception as e:
            self._on_exception(e)
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

        timeout_seconds = self._config.get('highwater.timeout') if not None else 30

        t = Timer(timeout_seconds, self.__do_highwater_timeout)
        t.start()

        while not (self._highwater_reached or self._is_highwater_timeout):
            msg = self._consumer.poll(1)

            logger.debug("__monitor_initial poll None: {}".format(msg is None))

            msgs = [msg] if msg is not None else None

            if msgs is not None:
                for msg in msgs:
                    self.__update_state(msg)

                    if msg.offset() + 1 == self._high:
                        self._highwater_reached = True

                self.__notify_changes()

        t.cancel()
        self._highwater_signal.set()

        if self._is_highwater_timeout:
            raise TimeoutException()
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
                self._highwater_reached = True

        consumer.assign(partitions)


class CachedTable(EventSourceTable):
    """
        Adds an in-memory cache to an EventSourceTable.   Caller should be aware of size of topic being consumed and
        this class should only be used for topics whose data will fit in caller's memory.

        This class is great for clients that want to grab all data in a topic, use it immediately, then done.  For
        example a shell script to dump contents of topic.

        This class can also be used by apps that want to do both: (1) grab all data up to highwater mark, and
        (2) continue monitoring for changes.  To do both register a CacheListener.

        The cached state is not copied, but shared via 'await_highwater_get()' and 'on_load()' to avoid wasting memory.

         Note:
             The configuration options above and beyond the ones in EventSourceTable include:

            +-------------------------+---------------------+-----------------------------------------------------+
            | Property Name           | Type                | Description                                         |
            +=========================+=====================+=====================================================+
            | ``caching.enabled``    | bool                 | If False, disables caching.  Default True.          |
            +-------------------------+---------------------+-----------------------------------------------------+

        The ability to disable caching is provided for subclasses that *usually* want an in-memory cache,
        but not always.

    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self._cache: Dict[Any, Message] = {}
        self._cache_listeners: List[CacheListener] = []

        super().__init__(config)

        caching_enabled = config.get('caching.enabled') if False else True

        if caching_enabled:
            self._listener = _CacheEventSourceListener(self, self._cache, self._cache_listeners)
            self.add_listener(self._listener)

    def add_cache_listener(self, listener: CacheListener) -> None:
        """
            Add a CacheListener.

            :param listener: The CacheListener to register
        """

        self._cache_listeners.append(listener)

    def remove_cache_listener(self, listener: CacheListener) -> None:
        """
            Remove a CacheListener.

            :param listener: The CacheListener to unregister
        """
        self._cache_listeners.remove(listener)

    def get(self) -> Dict[Any, Message]:
        """
            Returns the cache of compacted messages.

            See Also: 'await_highwater_get()' to block until highwater reached.

            :return: The cache of compacted messages
        """
        return self._cache

    def await_highwater_get(self) -> Dict[Any, Message]:
        """
            Block the calling thread and wait for topic highwater to be reached, then return cache of compacted
            messages.

            See: The 'highwater.timeout' option passed to the config Dict in constructor

            :return: The cache of compacted messages
            :raises TimeoutException: If highwater is not reached before timeout
        """
        self.await_highwater()
        return self._cache


class _CacheEventSourceListener(EventSourceListener):
    """
        Internal listener implementation for the CacheTable
    """

    def __init__(self, parent: CachedTable, cache: Dict[Any, Message], cache_listeners: List[CacheListener]) -> None:
        """
            Create a new _EventSourceCacheListener.

            :param cache: The cache
            :param cache_listeners: The cache listeners
        """
        self._parent = parent
        self._cache = cache
        self._cache_listeners = cache_listeners

    def __notify_load(self):
        for listener in self._cache_listeners:
            listener.on_load(self._cache)

    def __update_cache(self, msgs: List[Message]) -> None:
        """
            Merge (compact) updated set of unique messages with existing cache, replacing existing keys if any.

            :param msgs: The new messages
        """
        for msg in msgs:
            if msg.value() is None:
                if msg.key() in self._cache:
                    del self._cache[msg.key()]
            else:
                self._cache[msg.key()] = msg

        if self._parent.highwater_reached():
            for listener in self._cache_listeners:
                listener.on_update(msgs)

    def on_highwater(self) -> None:
        self.__notify_load()

    def on_highwater_timeout(self) -> None:
        pass

    def on_batch(self, msgs: List[Message]) -> None:
        self.__update_cache(msgs)
