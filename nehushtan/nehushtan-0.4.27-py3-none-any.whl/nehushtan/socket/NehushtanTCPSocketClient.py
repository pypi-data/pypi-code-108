import socket
from abc import abstractmethod
from typing import Optional


class NehushtanTCPSocketClient:
    """
    Since 0.4.16
    """

    def __init__(self, port: int, host=None):
        self.__listen_port = port
        self.__listen_host = host
        self.__socket_instance: Optional[socket.socket] = None

    def listen(self):
        address_entries = socket.getaddrinfo(
            self.__listen_host,
            self.__listen_port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        prepare_error = None

        for address_entry in address_entries:
            af, socktype, proto, canonname, sa = address_entry
            try:
                self.__socket_instance = socket.socket(af, socktype, proto)
                self.__socket_instance.connect(sa)
            except OSError as msg:
                prepare_error = msg
                if self.__socket_instance is not None:
                    self.__socket_instance.close()
                self.__socket_instance = None
                continue
            break

        if self.__socket_instance is None:
            raise prepare_error

        with self.__socket_instance:
            self.handle_client_conneciton()

    def get_connection(self):
        return self.__socket_instance

    @abstractmethod
    def handle_client_conneciton(self):
        """
        Override it to implement it with your own logic.
        """
        pass

    def close_connection(self):
        if self.__socket_instance is not None:
            self.__socket_instance.close()
        self.__socket_instance = None
