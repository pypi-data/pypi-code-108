from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable


class NehushtanHTTPService:
    """
    Since 0.4.0
    """

    def __init__(self):
        self.__server = None

    def get_server(self) -> HTTPServer:
        return self.__server

    def set_server(self, server: HTTPServer):
        self.__server = server
        return self

    def run(self, poll_interval=0.5):
        self.get_server().serve_forever(poll_interval=poll_interval)

    @staticmethod
    def run_with_selector_server(
            handler_class: Callable[..., BaseHTTPRequestHandler],
            listen_port: int,
            listen_host=''
    ):
        """
        USE HTTPServer
        This class builds on the TCPServer class by storing the server address
        as instance variables named server_name and server_port.
        The server is accessible by the handler, typically through the handler’s server instance variable.
        """
        server_address = (listen_host, listen_port)
        httpd = HTTPServer(server_address, handler_class)
        httpd.serve_forever()

    @staticmethod
    def run_with_threading_server(
            handler_class: Callable[..., BaseHTTPRequestHandler],
            listen_port: int,
            listen_host=''
    ):
        """
        USE ThreadingHTTPServer
        This class is identical to HTTPServer but uses threads to handle requests by using the ThreadingMixIn.
        This is useful to handle web browsers pre-opening sockets, on which HTTPServer would wait indefinitely.
        New in version 3.7.
        """
        server_address = (listen_host, listen_port)
        httpd = ThreadingHTTPServer(server_address, handler_class)
        httpd.serve_forever()
