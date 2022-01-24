# -*- coding:utf-8 -*-
import json

from confluent_kafka import cimpl
from kafka import (SimpleClient, KafkaConsumer)
from kafka.common import (OffsetRequestPayload, TopicPartition)
from confluent_kafka.admin import (AdminClient, NewTopic)


class KkOffset(object):
    def __init__(self, bootstrap_servers=None, topic=None, group_id=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.get_topic_offset = self._get_topic_offset
        self.get_group_offset = self._get_group_offset
        self.surplus_offset = self._surplus_offset

    @property
    def _get_topic_offset(self):  # topic的offset总和
        client = SimpleClient(self.bootstrap_servers)
        partitions = client.topic_partitions[self.topic]
        offset_requests = [OffsetRequestPayload(self.topic, p, -1, 1) for p in partitions.keys()]
        offsets_responses = client.send_offset_request(offset_requests)
        return sum([r.offsets[0] for r in offsets_responses])

    @property
    def _get_group_offset(self):  # topic特定group已消费的offset的总和
        consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                 group_id=self.group_id,
                                 )
        pts = [TopicPartition(topic=self.topic, partition=i) for i in
               consumer.partitions_for_topic(self.topic)]
        result = consumer._coordinator.fetch_committed_offsets(pts)
        return sum([r.offset for r in result.values()])

    @property
    def _surplus_offset(self) -> int:
        """
        :param topic_offset:     topic的offset总和
        :param group_offset:    topic特定group已消费的offset的总和
        :return: 未消费的条数
        """

        lag = self.get_topic_offset - self.get_group_offset
        if lag < 0:
            return 0
        return lag


def watch_topics(topic: str, bootstrap_servers: str):  # 查看所有话题
    consumer = KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers,
                             group_id=('',),
                             value_deserializer=json.loads,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             auto_commit_interval_ms=1000)
    return consumer.topics()


def create_topics(topic_list: list, bootstrap_servers: str):
    """
    :param
        host_port_and: 10.0.0.1:9092,10.0.0.2:9092,10.0.0.3:9092
    :type
        list: The split with "," and same as port
    :return:    create topics infos
    """
    a = AdminClient({'bootstrap.servers': bootstrap_servers})

    new_topics = [
        NewTopic(topic, num_partitions=3, replication_factor=1)
        for topic in topic_list
    ]

    fs = a.create_topics(new_topics)
    for topic, f in fs.items():
        try:
            f.result()  # result‘s itself 为空
            return {'status': True, 'data': f"创建成功: {topic}"}
        except cimpl.KafkaException:
            return {'status': True, 'data': "话题已存在"}
        except Exception as ex:
            return {'status': False, 'msg': f"请检查连接异常: {ex}"}
        finally:
            pass



