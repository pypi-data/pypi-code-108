# -*- coding:utf-8 -*-
from __future__ import absolute_import
from anti_useragent import UserAgent
import json
import re
import time
from kafka import KafkaProducer
import sys, os
sys.path.append(os.path.abspath('..'))
try:
    from module import logging
    from exceptions import KafkaInternalError
    from KafkaInstant import (KkOffset, create_topics, watch_topics)
except:
    from ..module import logging
    from ..exceptions import KafkaInternalError
    from ..KafkaInstant import (KkOffset, create_topics, watch_topics)

"""
:param 生产消息队列

:   传输时的压缩格式 compression_type="gzip"
    每条消息的最大大小 max_request_size=1024 * 1024 * 20
    重试次数 retries=3
"""


class KkProducer(KafkaProducer):
    pending_futures = []
    log = logging.get_logger('kafka_product')

    def __init__(self, options_name, try_max_times=3, *args, **kwargs):

        super(KkProducer, self).__init__(
            value_serializer=lambda m: json.dumps(m).encode('ascii'),
            retries=try_max_times, metadata_max_age_ms=10000000, request_timeout_ms=30000000, *args, **kwargs)
        self.topic = options_name
        self.try_max_times = try_max_times
        self.flush_now = self._flush

    def sync_producer(self, data_li: list or dict, partition=0, times: int = 0):
        """
            同步发送 数据
            :param data_li:  发送数据
            :return:
        """
        if not self.det_topic():
            raise KafkaInternalError(err_code=-1, err_msg='创建topic失败')
        if times > self.try_max_times:
            return False

        if not isinstance(data_li, list):
            future = self.send(self.topic, data_li, partition=partition)
            record_metadata = future.get(timeout=10)  # 同步确认消费
            partition = record_metadata.partition  # 数据所在的分区
            offset = record_metadata.offset  # 数据所在分区的位置
            print('save success：{0}, partition: {1}, offset: {2}'.format(record_metadata, partition, offset))

        for data in data_li:
            if not isinstance(data, dict):
                raise TypeError
            data.update({
                "options_name": self.topic,
                "data": data,
            })
            future = self.send(self.topic, data, partition=partition)
            record_metadata = future.get(timeout=10)  # 同步确认消费
            partition = record_metadata.partition  # 数据所在的分区
            offset = record_metadata.offset  # 数据所在分区的位置
            print('save success：{0}, partition: {1}, offset: {2}'.format(record_metadata, partition, offset))

    def asyn_producer_callback(self, data_li: list or dict, partition=0, times: int = 0):
        """
            异步发送数据 + 发送状态处理
            :param data_li:发送数据
            :return:
        """
        if not self.det_topic():
            raise KafkaInternalError(err_code=-1, err_msg='创建topic失败')
        if times > self.try_max_times:  # 异常数据
            self.log.debug(
                f'【数据丢失】：发送数据失败：{data_li}'
            )

            return False
        data_item = {
            "data": None,
            "queue_name": self.topic,
            "result": None,
        }
        try:
            if isinstance(data_li, list):
                for data in data_li:
                    if data and (len(data) > 0):
                        result = True
                    else:
                        result = False
                    data_item.update({"data": data, "result": result})

                    self.send(topic=self.topic, value=data_item, partition=partition).add_callback(
                        self.send_success, data_item).add_errback(self.send_error, data_item, times + 1, self.topic)
            else:
                data_item.update({"data": data_li})
                self.send(topic=self.topic, value=data_item, partition=partition).add_callback(
                    self.send_success, data_item).add_errback(self.send_error, data_item, times + 1, self.topic)
        except Exception as ex:
            raise KafkaInternalError(err_code=-1, err_msg=ex)
            # pass
        finally:
            self.flush()  # 批量提交
            # self.flush_now()  # 批量提交
            print('这里批量提交')

    def det_topic(self):
        create_topics([self.topic], bootstrap_servers=self.config['bootstrap_servers'])
        all_topic = watch_topics(self.topic, bootstrap_servers=self.config['bootstrap_servers'])
        if self.topic not in all_topic:
            create_topics([self.topic], bootstrap_servers=self.config['bootstrap_servers'])
            return False
        else:
            return True

    def origin_length(self, datas, max_nums: int = 1000000):  # 判断数据数量
        if not datas:
            return {'status': False, 'msg': u'数据为空'}
        if not isinstance(datas, list):
            return {'status': True, 'data': 1}
        if len(datas) > max_nums:


            return {'status': False, 'msg': u'批次数据量过大'}
        return {'status': True, 'data': len(datas)}

    @classmethod
    def send_success(*args, **kwargs):
        """异步发送成功回调函数"""
        print('save success is', args)
        return True

    @classmethod
    def send_error(*args, **kwargs):
        """异步发送错误回调函数"""
        print('save error', args)
        with open('/opt/ldp/{0}.json'.format(args[2]), 'a+', encoding='utf-8') as wf:
            json.dump(obj=args[0], fp=wf)
        return False

    def save_local(self, file_name: str, data_origin: dict):
        try:
            with open(
                f'{file_name}.json', 'a+', encoding='utf-8'
            ) as wf:
                json.dump(obj=data_origin, fp=wf)
        except Exception as ex:
            return ex

    @property
    def _flush(self, timeout=None):
        flush = super().flush(timeout=timeout)
        for future in self.pending_futures:
            if future.failed():
                # raise KafkaError(err_code='flush', err_msg='Failed to send batch')
                pass
            self.pending_futures = []
        return flush