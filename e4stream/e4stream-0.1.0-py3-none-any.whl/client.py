# Inspired by: https://github.com/HectorCarral/Empatica-E4-LSL
import socket
import logging
import os
import datetime 
from enum import Enum 

class Send(Enum):
    pass 

class Receive(Enum):
    pass 

class Command():
    SEND = Send
    RECEIVE = Receive
    COMMAND_PAUSE = "pause ON\r\n"
    COMMAND_RESUME = "pause OFF\r\n"
    COMMAND_DISCONNECT = "device_disconnect\r\n"
    COMMAND_LIST = "device_list\r\n"
    COMMAND_DEV_CONNECT = lambda device_id: f"device_connect {device_id}\r\n"
    COMMAND_SUBSCRIBE = lambda subscription: f"device_subscribe {subscription} ON\r\n"
    SUB_ACK_OK = lambda subscription: f'R device_subscribe {subscription} OK\n'
    DEV_ACK_OK = 'R device_connect OK\n'
    PAUSE_ON_ACK = 'R pause ON\n'
    PAUSE_OFF_ACK = 'R pause OFF\n'
    DISCONNECT_MESSAGE = "connection lost to device"


log_dir = 'logs/'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
logging.basicConfig(
    filename=os.path.join(log_dir, f'{log_name}.log'), 
    encoding='utf-8', 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', 
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

BUFFER_SIZE = 65536
TIMEOUT = 10
COMMAND_PAUSE = "pause ON\r\n"
COMMAND_RESUME = "pause OFF\r\n"
COMMAND_DISCONNECT = "device_disconnect\r\n"
COMMAND_LIST = "device_list\r\n"
COMMAND_DEV_CONNECT = lambda device_id: f"device_connect {device_id}\r\n"
COMMAND_SUBSCRIBE = lambda subscription: f"device_subscribe {subscription} ON\r\n"
SUB_ACK_OK = lambda subscription: f'R device_subscribe {subscription} OK\n'
DEV_ACK_OK = 'R device_connect OK\n'
PAUSE_ON_ACK = 'R pause ON\n'
PAUSE_OFF_ACK = 'R pause OFF\n'
DISCONNECT_MESSAGE = "connection lost to device"


class E4Client(object):
    def __init__(
        self, 
        address: str, 
        port: int, 
        device_id: str, 
        subscriptions,
        buffer_size: int = BUFFER_SIZE,
        timeout: int = TIMEOUT
    ):
        """
        Initialize parameters for E4 Client
        """
        self.address = address
        self.port = port
        self.device_id = device_id
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.running = False

        if isinstance(subscriptions, str):
            self.subscriptions = [subscriptions]
        elif isinstance(subscriptions, list):
            self.subscriptions = subscriptions
        else:
            logging.exception(f'Type {type(subscriptions)} unsupported for subscriptions input.')
        logging.info(f"Subscribing to the following streams: {self.subscriptions}")

        # Setup socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.timeout)
        logging.info(f"Setting up TCP socket at {address}:{port}")

    def reset(self):
        """
        Shutdown socket on port and reinit
        """
        logging.info(f'Resetting socket')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.timeout)
        self.connect()

    def connect(self):
        """
        Connect to E4 streaming server
        """
        logging.info('Connecting to server...')
        self.s.connect((self.address, self.port))
        self._connect_device()
        logging.info('Connected.')

        self._pause_stream()

        for sub in self.subscriptions:
            self.subscribe(sub)

    def reconnect(self):
        self.reset()
        self.connect()

    def run(self):
        self._resume_stream()
        self.running = True

    def pause(self):
        self._pause_stream()
        self.running = False

    def subscribe(self, subscription: str):
        logging.info(f"Suscribing to {subscription}...")
        self.s.send(COMMAND_SUBSCRIBE(subscription).encode())
        response = self.s.recv(self.buffer_size)
        
        if response.decode('utf-8') != SUB_ACK_OK(subscription):
            logging.exception(f'Could not subscripe to type {subscription}')

        logging.info('Subscribed successfully.')

    def disconnect(self):
        logging.info('Disconnecting...')
        self.s.send(COMMAND_DISCONNECT.encode())
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        logging.info('Disconnected.')

    def poll_for_tag(self):
        logging.info("Polling for tag...")
        while True:
            try:
                response = self._receive()
                packets = self._split_response(response)
                tag_timestamp = self._scan_for_tag(packets)
                if tag_timestamp is not None: 
                    return tag_timestamp
            except socket.timeout:
                logging.info("Timed out waiting for tag. Resuming polling...")

    def get_data(self):
        response = self.s.recv(self.buffer_size).decode("utf-8")
        if DISCONNECT_MESSAGE in response:
            logging.exception(f'Lost connection to device {self.device_id}.')
        packets = self._split_response(response)
        data_packets = [self._parse_packet(p) for p in packets if self._is_data_packet(p)]
        return data_packets # [(stream, timestamp, data)]

    def _pause_stream(self):
        """
        Pause data stream from E4 SS
        :return:
        """
        logging.info("Pausing data stream...")
        self.s.send(COMMAND_PAUSE.encode())
        response = self.s.recv(self.buffer_size)
        if response.decode('utf-8') != PAUSE_ON_ACK:
            logging.exception(f'Could not pause stream.')
        logging.info("Stream paused.")

    def _resume_stream(self):
        """
        Resume data stream from E4 SS
        :return:
        """
        logging.info("Resuming data stream...")
        self.s.send(COMMAND_RESUME.encode())
        response = self.s.recv(self.buffer_size)

    def _connect_device(self):
        """
        Connect to a specific device registered on the E4 SS
        """
        logging.info('Querying for available devices.')
        self.s.send(COMMAND_LIST.encode())
        
        response = self.s.recv(self.buffer_size)
        if self.device_id not in response.decode('utf-8'):
            logging.exception(f'Device ID {self.device_id} not in available devices.')
        
        logging.info('Connecting to device')
        self.s.send(COMMAND_DEV_CONNECT(self.device_id).encode())
        response = self.s.recv(self.buffer_size)
        if response.decode('utf-8') != DEV_ACK_OK:
            logging.exception(f'Could not subscribe to device {self.device_id}')
        logging.info('Device connected.')

    def _scan_for_tag(self, packets):
        for i, packet in enumerate(packets):
            if "E4_Tag" in packet:
                logging.info("Found tag.")
                return float(packet.split()[1].replace(',', '.'))
        return None

    def _split_response(self, response):
        return response.split("\n")

    def _receive(self):
        return self.s.recv(self.buffer_size).decode("utf-8")

    def _is_data_packet(self, packet):
        if packet == '': return False
        if packet[0] == 'R': return False
        return True

    def _parse_packet(self, packet):
        tokens = packet.split()
        stream = tokens[0]
        timestamp = float(tokens[1].replace(',', '.'))
        if stream == "E4_Acc":  # Special case
            data = (float(tokens[2].replace(',', '.')), float(tokens[3].replace(',', '.')), float(tokens[4].replace(',', '.')))
        else:
            data = float(tokens[2].replace(',', '.'))
        return stream, timestamp, data
