import socket
from abc import abstractmethod
from threading import Thread
from typing import Optional

from nehushtan.socket.SocketHandleThreadManager import SocketHandlerThreadManager


class NehushtanTCPSocketServer:
    """
    Since 0.4.16
    """

    def __init__(self, port: int, host=None, wait_queue_size=0, tm: SocketHandlerThreadManager = None):
        self.__listen_port = port
        self.__listen_host = host
        self.__socket_instance: Optional[socket.socket] = None
        self.__wait_queue_size = wait_queue_size
        if not tm:
            tm = SocketHandlerThreadManager()
        self.__thread_manager = tm

    def get_thread_manager(self):
        return self.__thread_manager

    def listen(self):
        address_entries = socket.getaddrinfo(
            self.__listen_host,
            self.__listen_port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
            0,
            socket.AI_PASSIVE
        )

        prepare_error = None

        for address_entry in address_entries:
            af, socktype, proto, canonname, sa = address_entry
            try:
                self.__socket_instance = socket.socket(af, socktype, proto)
                self.__socket_instance.bind(sa)
                self.__socket_instance.listen(self.__wait_queue_size)
            except OSError as msg:
                prepare_error = msg
                if self.__socket_instance is not None:
                    self.__socket_instance.close()
                self.__socket_instance = None
                continue
            break

        if self.__socket_instance is None:
            raise prepare_error

        # let accept could be interupted (Since 0.4.17)
        self.__socket_instance.settimeout(1)

        while not self.should_terminate():
            try:
                connection, address = self.__socket_instance.accept()
            except socket.timeout:
                continue

            thread = Thread(
                target=self.handle_incoming_connection,
                name=connection.getpeername(),
                args=(connection, address)
            )
            self.__thread_manager.register_thread(thread)
            thread.start()

    def should_terminate(self) -> bool:
        """
        If return True, stop the listener.
        Override it to implement it with your own logic.
        """
        return False

    @abstractmethod
    def handle_incoming_connection(self, connection: socket.socket, address):
        """
        IN THREAD.
        Override it to implement it with your own logic.
        You may need to close client connection inside
        """
        pass
