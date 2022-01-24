from time import time, sleep
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions, ConfigResource
import confluent_kafka


class Admin(AdminClient):
    def create_or_update_topic(self,
                               topic: str,
                               num_partitions: int,
                               replication_factor: int = None,
                               raw_configs: dict = None,
                               timeout: int = 10):
        if not raw_configs:
            raw_configs = {}

        topic_configs = self.get_topics_configs([topic, ])[topic]

        if not topic_configs:
            return self.create_topic_with_params(topic, num_partitions, replication_factor, raw_configs=raw_configs,
                                                 timeout=timeout)

        if topic_configs['num_partitions'] < num_partitions:
            self.set_topic_partitions(topic, num_partitions)

        is_equal_cnf = True
        for k, v in raw_configs.items():
            cur_val = topic_configs['raw_configs'][k]
            if not cur_val == str(v):
                is_equal_cnf = False

        if is_equal_cnf:
            return dict(result='ok')

        return self.set_topic_configs(topic, {k: str(v) for k, v in raw_configs.items()})

    def get_topics_configs(self, topics=None, timeout: int = 10):
        """
        :param topics: kafka topic names list
        :param timeout: request info timeout, seconds
        :return: params dict
        """

        topics_dict = self.list_topics(timeout=timeout).topics
        if not topics:
            topics = [t for t in topics_dict]

        if not topics:
            return {}

        topic_configs = {t: {} for t in topics}
        conf_request_list = []

        for topic in topics:
            topic_md = topics_dict[topic]
            # noinspection PyTypeChecker
            conf_request_list.append(ConfigResource('topic', topic))
            topic_configs[topic] = dict(num_partitions=len(topic_md.partitions),
                                        replication_factor=len(topic_md.partitions[0].replicas),
                                        raw_configs={})

        # noinspection PyTypeChecker
        fs = self.describe_configs(conf_request_list)

        # Wait for operation to finish.
        for res, f in fs.items():
            try:
                for conf_key, conf in f.result().items():
                    topic_configs[res.name]['raw_configs'][conf_key] = conf.value
            except confluent_kafka.KafkaException as e:
                print("Failed to describe {}: {}".format(res, e))
                raise
            except Exception:
                raise

        return topic_configs

    def create_topic_with_params(self,
                                 topic: str,
                                 num_partitions: int,
                                 replication_factor: int = None,
                                 raw_configs: dict = None,
                                 timeout: int = 10):

        topic_md = NewTopic(topic, num_partitions)

        if raw_configs:
            topic_md.config = raw_configs

        if replication_factor:
            topic_md.replication_factor = replication_factor

        fs = self.create_topics([topic_md, ])

        # Wait for operation to finish.
        # Timeouts are preferably controlled by passing request_timeout=15.0
        # to the create_topics() call.
        # All futures will finish at the same time.

        t = time()
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                while (time() - t) < timeout:
                    topics_dict = self.list_topics(timeout=10).topics
                    if topic in topics_dict:
                        print("Topic {} created".format(topic))
                        return dict(result='ok')

                    sleep(0.1)

                raise Exception(f'Timeout {timeout}s on creating topic {topic} expired')

            except confluent_kafka.KafkaException as e:
                if e.args[0].name() == 'TOPIC_ALREADY_EXISTS':
                    print("Topic {} ALREADY_EXISTS".format(topic))
                    return dict(result='ok')

                elif e.args[0].name() == 'INVALID_REPLICATION_FACTOR':
                    replication_factor = int(e.args[0].str().split('brokers:')[-1][:-1])
                    print(f"Topic {topic} will created with replication_factor = {replication_factor}")
                    return self.create_topic_with_params(topic, num_partitions, replication_factor, raw_configs,
                                                         timeout)
                else:
                    raise

            except Exception as e:
                print("Failed to create topic {}: {}".format(topic, e))
                raise

    def set_topic_configs(self, topic, raw_configs):
        # noinspection PyTypeChecker
        resource = ConfigResource('topic', topic)
        for k, v in raw_configs.items():
            resource.set_config(k, v)
            # print(k, v)

        fs = self.alter_configs([resource, ])

        for res, f in fs.items():
            try:
                f.result()  # empty, but raises exception on failure
                print("{} configuration successfully altered".format(res))
            except Exception:
                raise

        return {'result': 'ok'}

    def set_topic_partitions(self, topic: str, new_total_count: int):
        """
        :param topic:
        :param new_total_count: You can only set more partitions, than you already have
        :return: {'result': 'ok' | 'error'} dict
        """

        new_parts = [NewPartitions(topic, int(new_total_count))]

        # Try switching validate_only to True to only validate the operation
        # on the broker but not actually perform it.
        fs = self.create_partitions(new_parts, validate_only=False)

        # Wait for operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                print(f"Additional partitions created for topic {topic} now there are {new_total_count}")

            except Exception as e:
                print("Failed to add partitions to topic {}: {}".format(topic, e))
                raise

        return dict(result='ok')

    def set_topic_retention(self, topic: str, ms_retention: int = None, bytes_retention: int = None):
        """
        :param topic: topic
        :param ms_retention: retention time (retention.ms)
        :param bytes_retention: retention in bytes (retention.bytes)
        :return: {'result': 'ok' | 'error'} dict
        """
        if not (ms_retention or bytes_retention):
            return dict(result='ok')

        raw_configs = {}
        if ms_retention is not None:
            raw_configs['retention.ms'] = str(ms_retention)
        if bytes_retention is not None:
            raw_configs['retention.bytes'] = str(bytes_retention)

        return self.set_topic_configs(topic, raw_configs)
