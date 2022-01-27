# encoding: UTF-8
import json
import threading
import time
from datetime import datetime, timedelta
import redis

import schedule
import time

from rosetta_dispatcher.redis_client import RedisClient


class HeartbeatReporter:
    def __init__(self,
                 namespace: str,
                 service_name: str,
                 host_ip: str,
                 host_name: str,
                 redis_host: str,
                 redis_port: str,
                 password: str = None,
                 interval: int = 60):
        self.host_ip = host_ip
        self.host_name = host_name
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.running = False
        self.interval = interval
        self.namespace = namespace
        self.service_name = service_name
        self.client = RedisClient(host=redis_host, port=redis_port, password=password, decode_responses=True)

        schedule.every(self.interval).seconds.do(self.send_report)

        self.thread = threading.Thread(target=self.job_thread_fun)
        self.thread.daemon = True
        self.thread.start()

    def job_thread_fun(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def send_report(self):
        if self.running:
            r = self.client.conn

            data = {
                "service_name": self.service_name,
                "host_ip": self.host_ip,
                "host_name": self.host_name
            }

            mappings = {json.dumps(data, ensure_ascii=False): int(time.time())}
            r.zadd(self.namespace, mappings)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
