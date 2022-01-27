# encoding: UTF-8
import json
import threading
import time
from datetime import datetime, timedelta
from typing import List

import redis

import schedule
import time

from heartbeat.model.heartbeat_event import HeartbeatEvent, HeartbeatEventType
from rosetta_dispatcher.redis_client import RedisClient


class HeartbeatObserver:
    def __init__(self,
                 namespaces: List[str],
                 redis_host: str,
                 redis_port: str,
                 password: str = None,
                 interval: int = 60,
                 callback: callable = None):

        self.redis_host = redis_host
        self.redis_port = redis_port
        self.running = True
        self.interval = interval
        self.namespaces = namespaces
        self.client = RedisClient(host=redis_host, port=redis_port, password=password, decode_responses=True)

        schedule.every(self.interval).seconds.do(self.observe_report)
        self.thread = threading.Thread(target=self.job_thread_fun)
        self.thread.start()

        self.service_mapping = {namespace: {} for namespace in self.namespaces}
        self.callback = callback

    def job_thread_fun(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def observe_report(self):
        if self.running:
            r = self.client.conn
            now = int(time.time())
            for namespace in self.namespaces:
                if self.callback:
                    items = r.zrangebyscore(namespace, min=now - self.interval, max=now + 1, withscores=True)
                    newdict = {item[0]: item[1] for item in items}
                    newset = {item[0] for item in items}

                    olddict = self.service_mapping[namespace]
                    oldset = {key for key in olddict}

                    for stritem in newset - oldset:
                        server = json.loads(stritem)
                        event = HeartbeatEvent(event_type=HeartbeatEventType.NEW,
                                               namespace=namespace,
                                               service_name=server['service_name'],
                                               host_ip=server['host_ip'],
                                               host_name=server['host_name'],
                                               timestamp=newdict[stritem])
                        self.callback(event)

                    for stritem in oldset - newset:
                        server = json.loads(stritem)
                        event = HeartbeatEvent(event_type=HeartbeatEventType.LOST,
                                               namespace=namespace,
                                               service_name=server['service_name'],
                                               host_ip=server['host_ip'],
                                               host_name=server['host_name'],
                                               timestamp=olddict[stritem])
                        self.callback(event)

                    self.service_mapping[namespace] = newdict

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
