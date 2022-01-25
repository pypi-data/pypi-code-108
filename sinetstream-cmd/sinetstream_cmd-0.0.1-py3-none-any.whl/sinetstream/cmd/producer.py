import json
import socket
from pathlib import Path
from time import sleep
from argparse import ArgumentParser
from logging import getLogger
from sys import stderr
from sinetstream import MessageWriter

DEFAULT_SERVICE = "sensors"
DEFAULT_INTERVAL = 60
RETRY_INTERVAL = 60

DEFAULT_HOSTNAME = "raspberrypi"
PATH_RASPBERRYPI_SERIAL_NO = "/sys/firmware/devicetree/base/serial-number"

logger = getLogger(__name__)


class SimpleProducer(object):
    def __init__(self, callback, error_handler=None):
        self.callback = callback
        self.error_handler = (
            error_handler if error_handler else self._default_error_handler
        )
        self.retry = 0
        self._parse_args()
        if self.node_name is None:
            self.node_name = self._default_node_name()

    def run(self):
        while True:
            try:
                self._writer_loop()
            except Exception as e:
                self.error_handler(e)

    def _writer_loop(self):
        with MessageWriter(self.service) as writer:
            while True:
                data = self.callback()
                data["node"] = self.node_name
                msg = json.dumps(data)
                writer.publish(msg)
                if self.verbose:
                    print(msg, file=stderr)
                logger.debug(msg)
                sleep(self.interval)

    def _default_error_handler(self, err):
        if self.max_retry is None or self.retry < self.max_retry:
            logger.exception('Error in writer loop: retry=%d', self.retry)
            sleep(RETRY_INTERVAL)
            self.retry += 1
        else:
            raise

    def _default_node_name(self):
        hostname = socket.gethostname()
        if hostname == DEFAULT_HOSTNAME:
            sno = serial_no()
            if sno:
                return f"{DEFAULT_HOSTNAME}-{sno}"
        return hostname

    def _parse_args(self):
        parser = ArgumentParser(description="SINETStream Producer")
        parser.add_argument("-s", "--service", default=DEFAULT_SERVICE)
        parser.add_argument("-n", "--name", dest="node_name")
        parser.add_argument("-I", "--interval", type=int, default=DEFAULT_INTERVAL)
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("-R", "--retry", type=int, dest="max_retry", default=None)
        parser.parse_args(namespace=self)


def serial_no():
    p = Path(PATH_RASPBERRYPI_SERIAL_NO)
    if not p.exists():
        return None
    with p.open() as f:
        return f.read().rstrip("\u0000")
