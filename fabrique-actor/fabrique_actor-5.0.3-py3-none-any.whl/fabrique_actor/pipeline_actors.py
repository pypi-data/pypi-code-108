import confluent_kafka
from .env2configs import ProdConf, ConsConf
import signal

from .logger import Logger
import os

from fabrique_atelier.message import Message, MessageType, Header
from fabrique_atelier.constants import outgoing_fields, special_topics, VALID_ACTOR_TYPES
from fabrique_atelier.constants import MessageFieldsConstants as fld
from .actors import _get_messages2process

from time import time

import traceback

# hardcoded body fields for metrics and alerts
METRIC_FIELDS = [fld.error, fld.alerts, fld.metrics]

FABRIQUE_METRIC_COLLECTOR_TOPIC = os.getenv('FABRIQUE_METRIC_COLLECTOR_TOPIC', 'fabrique.monitor.in')


class Producer(confluent_kafka.Producer):
    def __init__(self, configs):
        super().__init__(configs)

    def send(self, topic_out, value, key=None):
        while True:
            try:
                self.produce(topic_out, value=value, key=key)
                break
            except BufferError:
                print('waiting for send buffer cleaning')
                self.flush()


class MessageBus(object):
    def __init__(self, _config_dict=None):
        """
        :param _config_dict: deprecated
        """
        self.metric_fields = METRIC_FIELDS
        self.client_id = os.getenv('HOSTNAME')
        self.pipeline_ver = os.getenv('PIPELINE_VERSION')
        self.pipeline_name = os.getenv('PIPELINE_NAME')
        self.actor_type = os.getenv('ACTOR_TYPE')

        # logger
        self.logger = Logger.make_logger(self.client_id)
        cons_conf = ConsConf()
        prod_conf = ProdConf(is_dispatcher=(self.actor_type == VALID_ACTOR_TYPES.dispatcher))

        self.topic_in = cons_conf.topic_in
        self.topic_out = prod_conf.topic_out
        self.topic_out_dict = prod_conf.topic_out_dict

        self.metrics_topic = FABRIQUE_METRIC_COLLECTOR_TOPIC

        self.running = True
        self.consumer = confluent_kafka.Consumer(cons_conf.configs)
        self.consumer.subscribe([self.topic_in, ])

        signal.signal(signal.SIGTERM, self.close)
        signal.signal(signal.SIGINT, self.close)

        self.consumer_num_messages = cons_conf.consumer_num_messages
        self.consumer_timeout_s = cons_conf.consumer_timeout_s

        self.producer = Producer(prod_conf.configs)

    def close(self, _arg1, _arg2):
        self.running = False

    def send_message(self, header, body, topic=None, message_type=None, kafka_key=None):
        """sends message with checking it type and using header info for special topics"""
        self.logger.debug('! send msg with session_id = {} to topic = {}'.format(header.session_id, topic))

        if not topic:
            return

        mes = None

        if topic == special_topics.end:
            # special case!
            topic = header.fabrique_out_topic
            mes = body['data']

            cur_time = time()

            self.send_monitor_metric(
                header, {'metrics': {
                    "api_session_complete_time": cur_time,
                    "api_session_delay": cur_time - header.session_start_time}
                }
            )

        else:
            if topic == special_topics.error:
                topic = header.fabrique_error_topic

            if topic == special_topics.metrics:
                topic = self.metrics_topic

            try:
                msg = Message.gen_message_by_header(header, body, message_type, self.client_id)
                mes = msg.serialize()
            except:
                print(f'!Cannot serialize message, {type(self).__name__}, {body}')

        try:
            if kafka_key:
                self.producer.send(topic, mes, kafka_key)
            else:
                self.producer.send(topic, mes)

        except TypeError:
            print(f'!Cannot send to {topic}, {type(self).__name__}, {mes.body}')
            raise

    def send_data(self, header, body, topic=None):
        if not topic:
            topic = self.topic_out

        if fld.data in body:
            mes = {}

            for field in outgoing_fields:
                if field in body:
                    mes[field] = body[field]

            if topic:  # for metric_reducer is empty
                kafka_key = body.get(fld.kafka_key)
                self.send_message(header, mes, topic=topic, message_type=MessageType.DATA.value, kafka_key=kafka_key)
        else:
            pass

        self.send_monitor_metric(header, body)

    def send_error(self, header, body, topic=None):
        if not header:
            header = Header('not-specified', MessageType.ERROR.value, self.client_id)

        if not topic:
            topic = special_topics.error

        if not topic:
            return

        assert 'error' in body

        self.send_message(header, body,
                          topic=topic, message_type=MessageType.ERROR.value)

        self.send_monitor_metric(header, body)

    def send_monitor_metric(self, header, body, topic=None):
        if not topic:
            topic = special_topics.metrics
        metric_body = {field: body[field] for field in self.metric_fields if field in body}

        if not metric_body:
            return

        if fld.timestamp in body:
            metric_body[fld.timestamp] = body[fld.timestamp]

        self.send_message(header, metric_body, message_type=MessageType.DATA.value, topic=topic)
        self.logger.info(f'! send metric with session_id = {header.session_id} to topic = {topic}: {metric_body}')


class Actor(MessageBus):

    def preprocess_msg(self, msg):
        """if None, nothing goes to callback"""

        try:
            message = Message.parse_mes(msg)
        except Exception:
            trace_msg = traceback.format_exc()
            error = '! Cannot parse message in {0!s}: {1!r}'.format(type(self).__name__, trace_msg)
            self.logger.error(error)
            print(msg)
            raise error

        if message.header.message_type != MessageType.DATA.value:
            return None

        return message

    def batch_callback(self, batch):
        out_batch = []
        for body in batch:
            try:
                out_body = self.body_callback(body)
            except:
                trace_msg = traceback.format_exc()
                error = "Exception in {0!s}: {1!r}".format(type(self).__name__, trace_msg)
                self.logger.error(error)
                out_body = body.copy()
                out_body['error'] = error
            out_batch.append(out_body)
        return out_batch

    def body_callback(self, body):
        raise Exception('body_callback method is not defined')

    def process_result(self, header, res_body):
        raise Exception('process_result method is not defined')

    def close_all(self):
        self.close(None, None)

    def process_messages(self, messages):

        errors_batch = []
        res_batch = []

        messages_batch = [[message.header, message.body] for message in
                          (self.preprocess_msg(mes) for mes in messages) if message]

        if not messages_batch:
            return False

        try:

            microbatch_size = len(messages_batch)
            start_time = time()

            headers, bodies = list(zip(*messages_batch))

            out_bodies = self.batch_callback(bodies)

            cur_time = time()
            microbatch_time = cur_time - start_time
            mean_per_mes_time = microbatch_time / microbatch_size

            if not out_bodies:
                return

            for i, body in enumerate(out_bodies):
                header = headers[i]
                if 'error' in body:
                    errors_batch.append([header, body])
                else:
                    if self.metrics_topic:
                        # additional metrics
                        if fld.metrics not in body:
                            body[fld.metrics] = {}
                        body[fld.metrics]['microbatch_size'] = microbatch_size
                        body[fld.metrics]['mean_per_mes_time'] = mean_per_mes_time
                        body[fld.metrics]['message_delay_time'] = microbatch_time
                        body[fld.metrics]['start_compute_time'] = start_time

                    res_batch.append([header, body])



        except Exception:
            trace_msg = traceback.format_exc()
            error = "Exception in {0!s}: {1!r}".format(type(self).__name__, trace_msg)
            self.logger.error(error)
            errors_batch = [[header, {'error': error}] for header, body in messages_batch]

        for header, body in res_batch:
            self.process_result(header, body)

        for header, body in errors_batch:
            self.send_error(header, body)

    def run(self):
        print(f'{self.client_id} started')
        try:
            while self.running:
                msgs = self.consumer.consume(num_messages=self.consumer_num_messages,
                                             timeout=self.consumer_timeout_s)
                if not msgs:
                    continue

                msgs2process = _get_messages2process(msgs)
                _ = self.process_messages(msgs2process)

        except KeyboardInterrupt:
            self.logger.warning("Aborted by user")

        except Exception:
            trace_msg = traceback.format_exc()
            self.logger.error("Exception: {0!r}".format(trace_msg))
            print(f'{trace_msg}')

        finally:
            print(f'{self.client_id} stopped')
            self.close_all()
            # Close down consumer to commit final offsets.
            self.consumer.close()
            print('consumer closed')


class Mapper(Actor):
    def process_result(self, header, res_body):
        self.send_data(header, res_body)


class Dispatcher(Actor):
    def process_result(self, header, res_body):
        dest_id = res_body.pop('destination', None)

        if not dest_id:
            error = "Exception in {0!s}: {1}".format(type(self).__name__, 'no "destination" field in result')
            self.send_error(header, {'error': error})
            return

        try:
            topic = self.topic_out_dict[dest_id]

        except:
            error = 'Exception in {0!s}: no topic in topic_dict for destination "{1}"'.format(type(self).__name__,
                                                                                              dest_id)
            self.send_error(header, {'error': error})
            return

        self.send_data(header, res_body, topic=topic)
