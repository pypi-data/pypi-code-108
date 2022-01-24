import socket
from abc import abstractmethod


class NehushtanUDPSocketClient:
    """
    Since 0.4.16
    """

    def __init__(self, host: str, port: int):
        self.__server_address = (host, port)
        self.__socket_instance: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def get_socket_instance(self):
        return self.__socket_instance

    def get_server_address(self):
        return self.__server_address

    @abstractmethod
    def handle_communication(self):
        """
        Override it to implement it with your own logic.
        use `self.__socket_instance.sendto(data, (self.__listen_host, self.__listen_port))`
        """
        pass

    def close_connection(self):
        if self.__socket_instance is not None:
            self.__socket_instance.close()
        self.__socket_instance = None
