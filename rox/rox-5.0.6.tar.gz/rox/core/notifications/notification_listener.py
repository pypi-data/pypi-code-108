import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests
import sseclient

from rox.core.logging.logging import Logging

CONNECTION_RETRY_INTERVAL_SEC = 3


class NotificationListener:
    def __init__(self, listen_url, app_key):
        self.listen_url = listen_url
        self.app_key = app_key
        self.process = None
        self.handlers = defaultdict(list)
        self.run_future = None
        self.cancel_event = None
        self.executor = None

    def on(self, event_name, handler):
        self.handlers[event_name].append(handler)

    def start(self):
        Logging.get_logger().debug('NotificationListener start called')
        self.cancel_event = threading.Event()
        sse_url = self.listen_url + ('/' if not self.listen_url.endswith('/') else '') + self.app_key
        self.executor = ThreadPoolExecutor(1)
        self.run_future = self.executor.submit(self.run, sse_url)
        
    def run(self, sse_url):
        Logging.get_logger().debug('NotificationListener run()')
        while True:
            if self.cancel_event.is_set():
                Logging.get_logger().debug('NotificationListener cancel event. without closing response')
                return
            try:
                with requests.get(sse_url, stream=True, headers={'Accept': 'text/event-stream'}, timeout=300) as response:
                    client = sseclient.SSEClient(response.iter_content())
                    for event in client.events():
                        for handler in self.handlers[event.event]:
                            Logging.get_logger().debug('NotificationListener calling event ' + event.event)
                            handler(event)
                        if self.cancel_event.is_set():
                            Logging.get_logger().debug('NotificationListener cancel event. closing response')
                            response.close()
                            return
                    
            except Exception:
                sleep(CONNECTION_RETRY_INTERVAL_SEC)

    def stop(self):
        Logging.get_logger().debug('NotificationListener stop called')
        self.run_future.cancel()
        self.cancel_event.set()
        self.executor.shutdown(wait=False)
        self.executor = None
        self.run_future = None
        Logging.get_logger().debug('NotificationListener stop finished')
