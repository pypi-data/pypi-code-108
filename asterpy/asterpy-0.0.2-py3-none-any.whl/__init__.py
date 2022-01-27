"""Simple python wrapper for controlling an aster account"""

import socket
import ssl
import json
import threading
from .user import User
from .channel import Channel
from .message import Message

DEBUG = True

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
        self.on_ready = None
        self.on_packet = None
        self.ssock = None
        self.self_uuid = 0
        self.current_channel = None
        self.channels = []
        self.name = ""
        self.pfp_b64 = ""

        #TODO this is terrible, make it better
        self.waiting_for = None
        self.waiting_data = None
        self.data_lock = threading.Condition()

        self.peers = {}
        self.running = True
        self.initialised = False

    def event(self, fn):
        setattr(self, fn.__name__, fn)
        return fn
        
    def __handle_packet(self, packet):
        # todo handle json decoding error
        if packet == "Goodbye": return
        packet = json.loads(packet)
        debug(f"Got packet, command {packet.get('command')}")
        if self.on_packet is not None:
            self.on_packet(packet)

        if self.waiting_for is not None and packet.get("command") == self.waiting_for:
            with self.data_lock:
                self.waiting_data = packet
                self.waiting_for = None
                self.data_lock.notify()
        
        if packet.get("command", None) is not None:
            if packet["command"] == "content":
                if self.on_message is not None:
                    self.on_message(Message(packet["content"], self.peers[packet["author_uuid"]], self.current_channel, packet["date"]))
            
            elif packet["command"] == "set":
                if packet["key"] == "self_uuid":
                    debug("Your UUID =", packet["value"])
                    self.self_uuid = packet["value"]

            elif packet["command"] == "metadata":
                for elem in packet["data"]:
                    elem_uuid = elem["uuid"]
                    if elem_uuid in self.peers:
                        self.peers[elem_uuid].update_from_json(elem)
                    else:
                        self.peers[elem_uuid] = User.from_json(elem)

            elif packet["command"] == "get_channels":
                for elem in packet["data"]:
                    self.__add_channel(elem)
                if self.current_channel is None:
                    self.join(self.channels[0])

            elif packet["command"] == "get_name":
                self.name = packet["data"]
            elif packet["command"] == "get_icon":
                self.pfp_b64 = packet["data"]

            elif packet["command"] == "history":
                pass #should already have been handled, if it needs to be

            else:
                debug("Got weird command", packet)

        if not self.initialised:
            if self.self_uuid != 0 and self.name != "" and self.pfp_b64 != "" and len(self.channels) > 0 and self.current_channel is not None:
                self.initialised = True
                if self.on_ready != None:
                    threading.Thread(target=self.on_ready).start() #TODO weird workaround, make it better

            #if self.self_uuid += 

    def send(self, message: str):
        self.ssock.send((message + "\n").encode("utf-8"))

    def disconnect(self):
        self.running = False
        self.send("/leave")

    def get_pfp(self, uuid):
        if uuid in self.peers:
            return self.peers[uuid].pfp

    def get_name(self, uuid):
        if uuid == self.self_uuid:
            return self.username
        if uuid in self.peers:
            return self.peers[uuid].username

    def get_channel(self, uuid):
        for channel in self.channels:
            if channel.uuid == uuid: return channel

    def get_channel_by_name(self, name):
        for channel in self.channels:
            if channel.name == name: return channel

    def __add_channel(self, data):
        self.channels.append(Channel(self, data["name"], data["uuid"]))

    def join(self, channel):
        if self.current_channel == channel:
            return
        self.send("/join " + channel.name)
        self.current_channel = channel

    def get_history(self, channel):
        orig_channel = self.current_channel
        self.join(channel)
        self.waiting_for = "history"
        with self.data_lock:
            self.send("/history 100")
            while self.waiting_data is None:
                self.data_lock.wait()

        packet = self.waiting_data
        self.waiting_data = None
        self.join(orig_channel)

        return [Message(elem["content"], self.peers[elem["author_uuid"]], channel, elem["date"]) for elem in packet["data"]]
 
    def run(self):
        context = ssl.SSLContext()
        with socket.create_connection((self.ip, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.ip) as ssock:
                self.sock = sock
                self.ssock = ssock
                if self.uuid is None:
                    ssock.send(b"/register\n")
                    ssock.send((f"/nick {self.username}\n/passwd {self.password}\n").encode("utf-8"))
                else:
                    ssock.send((f"/login {self.uuid}\n").encode("utf-8"))

                ssock.send("/get_all_metadata\n/get_channels\n/online\n/get_name\n/get_icon\n".encode("utf-8"))
                
                total_data = b""
                while self.running:
                    recvd_packet = ssock.recv(1024)
                    if not recvd_packet: break
                    total_data += recvd_packet
                    if b"\n" in total_data:
                        data = total_data.decode("utf-8").split("\n")
                        total_data = ("\n".join(data[1:])).encode("utf-8")
                        self.__handle_packet(data[0])
