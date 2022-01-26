import json
import inspect
import typing
import time
import requests
from abc import ABC

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from .config import KAFKA_SERVER_URL, REGISTER_URL
from .logger import init_logger
from .utils.utils import wait_until_server_is_online
from .event_utls.consumer_decorator import CONSUME_DESCRIPTOR_ATTR
from .event_utls.consumer_thread import ConsumerThread
from .event_utls.producer import Producer
from .message import Headers
from .topics import CONTROL_TOPIC
from .machine_topics import MACHINE_EVENTS
from .topics import IS_ALIVE
from .utils.TimerThread import TimerThread
from .message import Headers, AliveMessage

_logger = init_logger(__name__)


class Service(ABC):
    def __init__(self, name, **kwargs):
        self.name: str = name
        self.creation_timestamp = int(
            time.time() * 1000)  # The creation_timestamp is the number of milliseconds since the epoch (UTC).
        self.thread_pool: typing.List[ConsumerThread] = []
        self.control_log_consumer = None
        self._subscribed_topics: typing.List[str] = []
        self.producer = None
        self._consumer_decorator_metadata = {}
        for _, method in inspect.getmembers(self, inspect.ismethod):
            consumer_decorator_obj_set = getattr(
                method, CONSUME_DESCRIPTOR_ATTR, [])
            if consumer_decorator_obj_set:
                for consumer_decorator_obj in consumer_decorator_obj_set:
                    self._consumer_decorator_metadata[method.__name__] = consumer_decorator_obj
        self.kwargs = kwargs
        self.started = False  # if true the start() is processed successfully
        self.type = self.__class__.__name__
        self.category = ''
        self.status = "INIT"

    def to_json(self):
        return json.dumps({'name': self.name})

    @classmethod
    def from_json(cls, serialized_service_obj):
        service_obj_json = json.loads(serialized_service_obj)
        name = service_obj_json.get('name')
        if not name:
            raise ValueError('Key name is not in json object.')
        return cls(name)

    @property
    def subscribed_topics(self):
        if not self._subscribed_topics:
            for _, consumer_deco in self._consumer_decorator_metadata.items():
                for topic in consumer_deco.topics:
                    self._subscribed_topics.append(topic)
        return self._subscribed_topics

    def _control_log_handler(self, msg):
        _logger.debug(f"[{self.name}] call _control_log_handler")
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(
                f"[{self.name}] receive a message without a timestamp")
            return
        if timestamp < self.creation_timestamp:
            return
        message = json.loads(msg.value().decode('utf-8'))
        _logger.debug(
            f"[{self.name}] call _control_log_handler receive message: {message}")
        command = message.get('command')
        if self.name == message.get('name'):
            if command == "start":
                self.start()
            elif command == "stop":
                self.stop()

    def info(self) -> str:
        return "No info string is defined. The concrete service have to overload info()."

    def _create_consumer_threads(self):
        _logger.debug("_create_consumer_threads called.")
        for _, method in inspect.getmembers(self, inspect.ismethod):
            consumer_decorator_obj_set = getattr(
                method, CONSUME_DESCRIPTOR_ATTR, [])
            if consumer_decorator_obj_set:

                num_of_started_consumer = 0
                num_of_consumers = len(consumer_decorator_obj_set)

                def consumer_started_hook():
                    nonlocal num_of_started_consumer
                    num_of_started_consumer += 1
                    _logger.debug(f"consumer_started_hook called. counter: {num_of_started_consumer}, consumer: {num_of_consumers}.")
                    if num_of_started_consumer == num_of_consumers:
                        self.status = "RUNNING"
                        _logger.debug(self.status)

                for consumer_decorator_obj in consumer_decorator_obj_set:
                    print(f"topic in create: {consumer_decorator_obj.get_topics()}")
                    self.thread_pool.append(
                        ConsumerThread(consumer_decorator_obj.get_topics(),
                                       self.type,
                                       consumer_decorator_obj.bootstrap_server,
                                       method, consumer_started_hook, **self.kwargs) if self.kwargs else ConsumerThread(
                            consumer_decorator_obj.get_topics(),
                            self.type,
                            consumer_decorator_obj.bootstrap_server,
                            method, consumer_started_hook))

    def post_init(self):
        _logger.debug("call post_init")
        self.producer.wait_until_topics_created([IS_ALIVE], poll_time=1, max_iterations=30)
        self.alive_thread = TimerThread(0.1, self._alive)
        self.alive_thread.start()

    def _alive(self):
        self.producer.async_produce(topic=IS_ALIVE, value=AliveMessage(info=self.info(), type=self.type, status=self.status, category=self.category).serialize(), headers=Headers(self.name))

    def init_local(self):
        _logger.debug(f"[{self.name}] call init_local")

        # Register process
        wait_until_server_is_online(REGISTER_URL, logger=_logger)
        res = requests.get(f"http://{REGISTER_URL}/register/{self.name}")
        _logger.debug(f"receive status code {res.status_code}")
        _logger.debug(f"error: {res.content}")
        if res.status_code != 200:
            raise Exception(f"Registration of service failed. An service with the name {self.name} is already running/")
        self.producer = Producer()

        wait_until_server_is_online(url=KAFKA_SERVER_URL, logger=_logger)
        # wait maximal ~30s to let topics be created. Just for startup
        self.producer.wait_until_topics_created([CONTROL_TOPIC, MACHINE_EVENTS], poll_time=1, max_iterations=30)

        self.control_log_consumer = ConsumerThread(topics=[CONTROL_TOPIC], group_id=self.name + "_" + CONTROL_TOPIC,
                                                   bootstrap_server=KAFKA_SERVER_URL,
                                                   message_handler=self._control_log_handler, consumer_started_hook=None)

        self.control_log_consumer.start()
        self.control_log_consumer.wait_until_ready()

        self._create_consumer_threads()

        self.start()

        self.post_init()
        _logger.debug(f"[{self.name}] exit init_local")

        # wait until stop() is executed.
        self.control_log_consumer.join()

    def start(self):
        _logger.debug(f"[{self.name}] call start.")
        for thread in self.thread_pool:
            if not thread.is_alive():
                _logger.debug(f"[{self.name}] start thread: {thread.name}")
                thread.start()
                thread.wait_until_ready()
        self.started = True
        _logger.debug(f"[{self.name}] exit start.")

    def stop(self):
        _logger.debug(f"stop is called on service {self.name}")
        for thread in self.thread_pool:
            if thread.is_alive():
                thread.stop()
                thread.join()

        if self.alive_thread:
            self.alive_thread.stop()
            self.alive_thread.join()

        # note: .join() is already called in init_local which is called mainThread
        self.control_log_consumer.stop()

    def send(self, topic, message, headers):
        _logger.debug(f"[{self.name}] call send {str(headers)}")
        self.producer.sync_produce(topic=topic,
                                   value=message.serialize(),
                                   headers=headers)

    # used for pickle class
    def __getstate__(self):
        odict = {'name': self.name}
        return odict

    # used for pickle class
    def __setstate__(self, state):
        kwargs = {}
        self.__dict__ = type(self)(state['name'], **kwargs).__dict__
