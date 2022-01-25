import json
import platform
import logging.handlers
from datetime import datetime
from confluent_kafka import Producer
import logging
from threading import Thread
from queue import Queue
import requests
import os
import yaml


def read_config(path_config: str, method: str):
    try:
        with open(path_config, 'r') as yml_file:
            _config = yaml.load(yml_file)

            if method in _config:
                return _config[method]

    except Exception as ex:
        print(ex)

    return None


class SageKafka(logging.Handler):
    def __init__(self, env: str, system: str, group: str, bootstrap_servers: str, project: str, level: str = 'DEBUG'):
        logging.Handler.__init__(self)
        self.bootstrap_servers = bootstrap_servers
        self.required_fields = {
            'env': env,
            'group': group,
            'system': system,
            # 'project': project,
            'inst': os.environ.get('HOST', platform.uname()[1]),
        }
        self.topic = f'sage-logs-{group}'
        self.project = project
        self._producer = Producer(
            {'bootstrap.servers': self.bootstrap_servers,
             'client.id': f'{group}_logs'}
        )

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {self.topic} - {msg.topic()} [{msg.partition()}]')

    def emit(self, dst_info):
        try:
            _level = dst_info.msg.split('|')[1]
            _msg = dst_info.msg.split('|', 2)[2].split(' - ', 1)[1]

            _data = {'project': self.project, 'logger_level': _level.strip(), 'msg': _msg}

            send_info = self.required_fields.copy()
            send_info.update(_data)

            if 'extra' in dst_info.extra and dst_info.extra['extra'] is not None:
                send_info.update(dst_info.extra['extra'])

            send_info["@timestamp"] = datetime.utcnow().isoformat()[:-3] + 'Z'

            self._producer.produce(self.topic, json.dumps(send_info), callback=self.delivery_report)
            self._producer.poll(0.1)

        except BufferError as e:
            print('BufferError', e)
            self._producer.poll(2)
            self._producer.flush()

        except Exception as e:
            print('Exception', e)
            self._producer.poll(0.1)

    def close(self):
        self._producer.flush()
        logging.Handler.close(self)


class SageRest(logging.Handler):
    def __init__(self, env: str, system: str, group: str, project: str, host: str, threads: int = 2,
                 level: str = 'DEBUG', dir_path: str = None):
        logging.Handler.__init__(self)

        self.required_fields = {
            'env': env,
            'group': group,
            'system': system,
            # 'project': project,
            'inst': os.environ.get('HOST', platform.uname()[1]),
        }
        self.topic = f'sage-logs-{group}'
        self.project = project
        self.host = host
        self.queues = Queue()
        self.threads = threads
        self.create_q()
        self.dir_path = dir_path
        self.session = requests.Session()

    def _send_text(self, idx, queue):
        _host = self.host
        while True:
            try:
                data = queue.get()

                if self.dir_path is None:
                    r = self.session.post(self.host, timeout=3, data={'msg': json.dumps(data, ensure_ascii=False)})
                    print(self.host, r)
                else:
                    _data = read_config(os.path.join(self.dir_path, 'config.yml'), 'sageRest')
                    print(_data)
                    if _data is not None and 'request' in _data and _data['request']:
                        if 'restHost' in _data:
                            _host = _data['restHost']

                        r = self.session.post(_host, timeout=3, data={'msg': json.dumps(data, ensure_ascii=False)})
                        print(_host, r)
                    else:
                        print('request false!')

            except Exception as ex:
                print('send_text', _host, ex)

            finally:
                queue.task_done()

    def create_q(self):
        for idx in range(self.threads):
            worker = Thread(target=self._send_text, args=(idx, self.queues))
            worker.setDaemon(True)
            worker.start()

    def emit(self, dst_info):
        try:
            _level = dst_info.msg.split('|')[1]
            _msg = dst_info.msg.split('|', 2)[2].split(' - ', 1)[1]

            _data = {'project': self.project, 'logger_level': _level.strip(), 'msg': _msg}

            send_info = self.required_fields.copy()
            send_info.update(_data)

            if 'extra' in dst_info.extra and dst_info.extra['extra'] is not None:
                send_info.update(dst_info.extra['extra'])

            send_info["@timestamp"] = datetime.utcnow().isoformat()[:-3] + 'Z'
            self.queues.put(send_info)

        except Exception as e:
            print(e)

    def close(self):
        self.queues.join()
        logging.Handler.close(self)
