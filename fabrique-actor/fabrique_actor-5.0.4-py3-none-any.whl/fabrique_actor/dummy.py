# flake8: noqa: E402 
import sys

# get&set selected/default constants
# DUMMY_TOPIC_IN = os.getenv('TOPIC_IN', 'topic_in')
# DUMMY_TOPIC_OUT = os.getenv('TOPIC_OUT', 'topic_out')
# DUMMY_TOPIC_OUT_DICT = os.getenv('TOPIC_OUT_DICT', '{"odd": "topic_odd", "even": "topic_even"}')
# os.environ['TOPIC_OUT'] = DUMMY_TOPIC_OUT
# os.environ['TOPIC_IN'] = DUMMY_TOPIC_IN
# os.environ['TOPIC_OUT_DICT'] = DUMMY_TOPIC_OUT_DICT

DUMMY_FABRIQUE_METRIC_COLLECTOR_TOPIC = 'fabrique.monitor.in'

from unittest import mock
from fabrique_atelier.dummy.store import Store

confluent_kafka_mock = mock.Mock()
confluent_kafka_mock.admin = mock.Mock()

sys.modules['confluent_kafka'] = confluent_kafka_mock
sys.modules['confluent_kafka.admin'] = confluent_kafka_mock.admin


class DumbProducer:
    def __init__(self, *_args, **_kwargs):
        self.store = None

    def set_store(self, store):
        self.store = store

    def produce(self, topic, value, key=None):
        assert hasattr(self, 'store'), 'you must set_store before send!'
        self.store.produce(topic, value, key)


class DumbConsumer:
    def __init__(self, *_args, **_kwargs):
        self.store = None
        self.subscribed_topics = []

    def set_store(self, store):
        self.store = store

    def subscribe(self, topic_list):
        self.subscribed_topics = topic_list

    # noinspection PyUnusedLocal
    def consume(self, num_messages=10, timeout=1.0):
        assert hasattr(self, 'store'), 'you must set_store before consume!'

        _, topic2len = self.store.get_topic_lens()
        sum_topics = sum((topic2len.get(topic, 0) for topic in self.subscribed_topics))
        if not sum_topics:
            raise StopIteration

        for topic in self.subscribed_topics:
            if topic2len.get(topic):
                return next(self.store.reader_generator(topic, max_values=num_messages))
        return []

    @staticmethod
    def close():
        print('Consumer is closed')
        # os._exit(0)


confluent_kafka_mock.Consumer = DumbConsumer
confluent_kafka_mock.Producer = DumbProducer

from fabrique_actor.actors import Processor, Emitter, Collector, Dispatcher


def post_init(self, *_args, **_kwargs):
    print('Work with Dummy StandaloneActor')
    self.store = Store()

    if self.consumer:
        self.consumer.set_store(self.store)

    self.producer.set_store(self.store)


class DummyLogger:
    def __init__(self):
        self.logs_info = []
        self.logs_debug = []
        self.logs_error = []

    def clear(self):
        self.logs_info = []
        self.logs_debug = []
        self.logs_error = []

    def info(self, mes, *_args, **_kwargs):
        self.logs_info.append(mes)

    def debug(self, mes, *_args, **_kwargs):
        self.logs_debug.append(mes)

    def error(self, mes, *_args, **_kwargs):
        self.logs_error.append(mes)


sys.modules['confluent_kafka.admin'] = confluent_kafka_mock.admin


# noinspection PyUnusedLocal
def start(self, *_args, **_kwargs):
    try:
        # noinspection PyUnusedLocal
        self.raw_perpetual_start()
    except StopIteration:
        pass


for actor in [Processor, Emitter, Collector, Dispatcher]:
    # actor.store = None  # init store for IDE
    actor.post_init = post_init  # set store method
    actor.raw_perpetual_start = actor.start
    actor.start = start

sys.modules['fabrique_actor.actors.Emitter'] = Emitter
sys.modules['fabrique_actor.actors.Collector'] = Collector
sys.modules['fabrique_actor.actors.Dispatcher'] = Dispatcher
sys.modules['fabrique_actor.actors.Processor'] = Processor
