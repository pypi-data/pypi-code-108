import socket
import threading
import errno
from queue import Queue

from biolib.typing_utils import Optional


class SocketListenerThread(threading.Thread):
    DEFAULT_BUFFER_SIZE = 1024

    def __init__(self, socket_connection: socket.socket, message_queue: Queue):
        threading.Thread.__init__(self, daemon=True)

        self.socket_connection = socket_connection
        self.message_queue = message_queue

    def run(self) -> None:
        while True:
            try:
                next_package_length_as_bytearray = self._receive_specific_byte_length(8)
            except IOError as exception:
                # [Errno 9] Bad file descriptor
                if exception.errno == errno.EBADF:
                    break
                else:
                    raise exception

            if next_package_length_as_bytearray is not None:
                next_package_length_as_int = int.from_bytes(next_package_length_as_bytearray, 'big')
                package = self._receive_specific_byte_length(next_package_length_as_int)
                self.message_queue.put(package)

    def _receive_specific_byte_length(self, byte_length_to_receive: int) -> Optional[bytearray]:
        return_data = bytearray()

        while len(return_data) < byte_length_to_receive:
            byte_length_left_to_receive = byte_length_to_receive - len(return_data)
            packet = self.socket_connection.recv(min(self.DEFAULT_BUFFER_SIZE, byte_length_left_to_receive))
            if not packet:
                return None
            return_data.extend(packet)

        return return_data
