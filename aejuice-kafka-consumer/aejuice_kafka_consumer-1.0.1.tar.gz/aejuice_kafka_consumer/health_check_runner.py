import os

from http.server import HTTPServer
from threading import Thread
from .health_check import HealthCheck, state_storage


class HealthCheckRunner(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.httpd = None

    def run(self):
        self.httpd = HTTPServer((os.getenv("HTTP_HOST"), int(os.getenv("HTTP_PORT"))), HealthCheck)
        self.httpd.serve_forever()

    def set_ready_state(self, state: bool):
        return state_storage.set_ready_state(state)
