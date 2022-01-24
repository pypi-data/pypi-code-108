#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Socket to mime a Telnet server for the tests
"""
import logging
import socket
import threading
from abc import abstractmethod
from builtins import super
from time import sleep
from typing import Optional

logging.basicConfig(level=logging.DEBUG)


class LocalTelnetTestServer:
    """
    Local Telnet Sever for testing
    """

    def __init__(self, port=23, timeout=1):
        self._host = ""  # "127.0.0.1"
        self._port = port
        self._timeout = timeout
        self._s = socket.socket()
        self._client = None
        self._addr = None
        logging.debug("LocalTelnetTestServer created")
        logging.debug("Bind...")
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.bind((self._host, self._port))
        logging.debug("Start listen")
        self._s.listen()

    def __del__(self):
        _s = getattr(self, "_s", None)
        if _s is not None:
            _s.close()
            del _s

    def open(self):
        logging.debug("Accepting?")
        self._s.settimeout(self._timeout)
        self._client, self._addr = self._s.accept()
        logging.debug(f"Accepted: {self._client} with {self._addr}")
        self._client.settimeout(self._timeout)

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    def put_text(self, text: str, encoding=None):
        if encoding is None:
            self._client.send(text.encode())
        else:
            self._client.send(text.encode(encoding=encoding))

    def get_written(self):
        # logging.debug("Receiving")
        try:
            data = self._client.recv(1024)
            # logging.debug(f"Received: {data}")
            return data.decode().strip()
        except socket.timeout:
            return None


class TechnixMockup:
    def __init__(self):

        self.status: int = 0
        self.keep_running: bool = True
        self.listen_and_repeat = [
            "P5,0",
            "P5,1",
            "P6,0",
            "P6,1",
            "P7,0",
            "P7,1",
            "P8,0",
            "P8,1",
        ]

        self.voltage: Optional[int] = None
        self.current: Optional[int] = None

        self.last_request = ""
        self.custom_answer = ""

        self._x = threading.Thread(target=self.listen_and_answer)

    @abstractmethod
    def get_written(self):
        return ""

    @abstractmethod
    def put_text(self, request):
        pass

    def listen_and_answer(self):
        while self.keep_running:
            request = self.get_written()
            if not request:
                continue

            logging.debug(f"TechnixMockup got: {request}")

            if request == "E":
                self.put_text(f"E{self.status}")
            elif request in self.listen_and_repeat:
                self.put_text(request)
                logging.debug(f"TechnixMockup returned the request: {request}")
            elif self.voltage and request == "a1":
                self.put_text(f"a1{self.voltage}")
            elif self.current and request == "a2":
                self.put_text(f"a2{self.current}")
            else:
                self.last_request = request
                self.put_text(self.custom_answer)

            sleep(0.01)


class LocalTechnixServer(TechnixMockup):
    def __init__(self, port=4660, timeout=1):
        super().__init__()
        self._ts = LocalTelnetTestServer(port=port, timeout=timeout)

    def open(self):
        self._ts.open()
        self._x.start()

    def close(self):
        self.keep_running = False
        self._x.join()
        self._ts.close()

    def get_written(self):
        return self._ts.get_written()

    def put_text(self, request, encoding=None):
        self._ts.put_text(text=request, encoding=encoding)


class T560Mockup:
    def __init__(self):
        self.status: int = 0
        self.keep_running: bool = True
        self.response = "OK"
        self._x = threading.Thread(target=self.listen_and_answer)
        self.auto_install_check = "AU"
        self.auto_install_response = "1"
        self.channel_check = ["AS", "BS", "CS", "DS"]
        self.channel_response = \
            "Ch  A  POS  ON  Dly  00.000,000,000,000  Wid  00.000,000,000,000"
        self.error_check = "Throw an error"
        self.error_response = "??"
        self.trigger_check = "TR"
        self.trigger_response = \
            "Trig REM HIZ Level 1.250 Div 0000000000 SYN 00010000.00"
        self.gate_check = "GA"
        self.gate_response = "Gate OFF POS HIZ Shots 0000000066"

    @abstractmethod
    def get_written(self):
        return ""

    @abstractmethod
    def put_text(self, request):
        pass

    def listen_and_answer(self):
        while self.keep_running:
            request = self.get_written()
            if not request:
                continue
            if request in self.channel_check:
                self.put_text(self.channel_response)
            elif request == self.trigger_check:
                self.put_text(self.trigger_response)
            elif request == self.gate_check:
                self.put_text(self.gate_response)
            elif request == self.error_check:
                self.put_text(self.error_response)
            elif request == self.auto_install_check:
                self.put_text(self.auto_install_response)
            else:
                self.put_text(self.response)
            sleep(0.01)


class LocalT560Server(T560Mockup):
    def __init__(self, port=9999, timeout=1):
        super().__init__()
        self._ts = LocalTelnetTestServer(port=port, timeout=timeout)

    def open(self):
        self._ts.open()
        self._x.start()

    def close(self):
        self.keep_running = False
        self._x.join()
        self._ts.close()

    def get_written(self):
        return self._ts.get_written()

    def put_text(self, request, encoding=None):
        self._ts.put_text(text=request, encoding=encoding)
