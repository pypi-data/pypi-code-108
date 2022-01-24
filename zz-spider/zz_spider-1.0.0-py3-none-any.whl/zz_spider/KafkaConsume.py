import json
import os
import re
import time
import threading, multiprocessing
from kafka import KafkaConsumer
from KafakProduct import KkProducer
from module import logging


class SavePipeline:
    """
    :parameter data save pipeline as file
    :param save_data to localfile.json
    """

    def __init__(self, file_name, log_path=os.path.abspath(os.path.dirname(os.getcwd())) + '/'):
        self.log_path = log_path
        self.file_name = file_name

    def __setitem__(self, key, value):
        return getattr(key, value)

    def __getitem__(self, item):
        return self

    def save_data(self, doing_type: str = 'a+', data_item: dict = lambda d: json.loads(d)):
        """
        数据存储
        :param doing_type: str
        :param data_item: dict
        :return: 写入json文件
        """
        whole_path = self.log_path + '{0}.json'.format(self.file_name)
        print(whole_path, 'A' * 20)
        try:
            with open(whole_path, doing_type, encoding='utf-8') as wf:
                result = wf.write(json.dumps(data_item) + '\n')
            if not result:
                return {'status': False, 'msg': '写入失败'}
            return {'status': True, 'data': '写入成功'}
        except Exception as e:
            return {'status': False, 'msg': str(e)}
        finally:
            pass


class KafkaReceive(threading.Thread):
    log = logging.get_logger('kafka_consume')
    
    def __init__(self, bootstrap_servers, topic, group_id, client_id=''):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.client_id = client_id
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                 group_id=self.group_id,
                                 auto_offset_reset='latest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe([self.topic])
        sucess_is = 0
        error_is = 0
        get_list = []
        for msg in consumer:
            self.log.info(f'topic: {msg.topic}')
            self.log.info(f'partition: {msg.partition}')
            self.log.info(f'key: {msg.key}; value: {msg.value}')
            self.log.info(f'offset: {msg.offset}')

            msg_item = json.loads(json.dumps(msg.value.decode('utf-8')))
            result = SavePipeline(self.topic).save_data(data_item=msg_item)
            if result.get('status', False):
                sucess_is += 1
            else:
                error_is += 1
            get_list.append(msg_item)
        consumer.close()

        return sucess_is, error_is, get_list


def restart_program():

    import sys
    python = sys.executable
    os.execl(python, python, * sys.argv)


def task(bootstrap_servers, topic, times_count: int = 4):
    from KafkaInstant import KkOffset
    offset = KkOffset(
        bootstrap_servers=bootstrap_servers, topic=topic, group_id=topic
    )
    print(offset.surplus_offset, type(offset.surplus_offset))

    import time

    tasks = [
        KafkaReceive(
            bootstrap_servers=bootstrap_servers, topic=topic,
            group_id=topic)
        for c in range(times_count)
    ]

    for t in tasks:
        t.start()

    time.sleep(10)

    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()


if __name__ == '__main__':
    # task()
    KafkaReceive(
        bootstrap_servers='', topic='',
        group_id='').run()