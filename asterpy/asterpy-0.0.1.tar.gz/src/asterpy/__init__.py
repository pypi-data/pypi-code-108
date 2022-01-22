"""Simple python wrapper for controlling an aster account"""

import socket
import ssl
import json
from .user import User
from .channel import Channel
from .message import Message

DEBUG = False

def debug(*args):
    if DEBUG:
        print(*args)

class Client:
    """Represents a client connection to one server"""
    def __init__(self, ip: str, port: int, username: str, password: str, uuid=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.uuid = uuid
        self.on_message = None
        self.on_ready: Function = None
        self.ssock = None

    def event(self, fn):
        setattr(self, fn.__name__, fn)
        return fn
        
    def handle_packet(self, packet):
        # todo handle json decoding error
        packet = json.loads(packet)
        debug(packet)
        if packet.get("content", None) is not None:
            if self.on_message is not None:
                self.on_message(Message(packet["content"], None, Channel(self, "general")))

        if packet.get("command", None) is not None:
            if packet["command"] == "set":
                if packet["key"] == "self_uuid":
                    debug("Your UUID =", packet["value"])

            else:
                debug("Got weird command", packet)

    def send(self, message: str):
        self.ssock.send((message + "\n").encode("utf-8"))

    def run(self):
        context = ssl.SSLContext()

        with socket.create_connection((self.ip, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.ip) as ssock:
                self.ssock = ssock
                if self.uuid is None:
                    ssock.send(b"/register\n")
                else:
                    ssock.send((f"/login {self.uuid}\n").encode("utf-8"))
                ssock.send((f"/nick {self.username}\n/passwd {self.password}\n").encode("utf-8"))
                if self.on_ready is not None:
                    self.on_ready()
                
                total_data = b""
                while True:
                    total_data += ssock.recv(1024)
                    if b"\n" in total_data:
                        data = total_data.decode("utf-8").split("\n")
                        total_data = ("\n".join(data[1:])).encode("utf-8")
                        self.handle_packet(data[0])
