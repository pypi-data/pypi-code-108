import socket
from abc import abstractmethod
from threading import Thread
from typing import Optional

from nehushtan.socket.SocketHandleThreadManager import SocketHandlerThreadManager


class NehushtanUDPSocketServer:
    """
    Since 0.4.16
    """

    def __init__(self, host: str, port: int, buffer_size=0, tm: SocketHandlerThreadManager = None):
        self.__listen_port = port
        self.__listen_host = host
        self.__socket_instance: Optional[socket.socket] = None
        if buffer_size <= 0:
            buffer_size = 1024
        self.__buffer_size = buffer_size
        if not tm:
            tm = SocketHandlerThreadManager()
        self.__thread_manager = tm

    def get_thread_manager(self):
        return self.__thread_manager

    def get_socket_instance(self):
        return self.__socket_instance

    def listen(self):
        self.__socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket_instance.bind((self.__listen_host, self.__listen_port))

        while not self.should_terminate():
            data, address = self.__socket_instance.recvfrom(self.__buffer_size)

            thread = Thread(target=self.handle_incoming_data, name=address, args=(data, address))
            self.__thread_manager.register_thread(thread)
            thread.start()

    def should_terminate(self) -> bool:
        """
        If return True, stop the listener.
        Override it to implement it with your own logic.
        """
        return False

    @abstractmethod
    def handle_incoming_data(self, data: bytes, address):
        pass
