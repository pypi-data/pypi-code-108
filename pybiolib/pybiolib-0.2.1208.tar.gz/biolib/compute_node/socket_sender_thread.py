import socket
import threading
import errno
from queue import Queue


class SocketSenderThread(threading.Thread):
    DEFAULT_BUFFER_SIZE = 1024

    def __init__(self, socket_connection: socket.socket, message_queue: Queue):
        threading.Thread.__init__(self, daemon=True)

        self.socket_connection = socket_connection
        self.message_queue = message_queue

    def run(self) -> None:
        while True:
            message = self.message_queue.get()
            payload = bytearray()
            payload.extend(len(message).to_bytes(length=8, byteorder='big', signed=False))
            payload.extend(message)
            try:
                self.socket_connection.sendall(payload)
            except IOError as exception:
                # [Errno 9] Bad file descriptor
                if exception.errno == errno.EBADF:
                    break
                else:
                    raise exception

            self.message_queue.task_done()
