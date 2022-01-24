from abc import abstractmethod

from nehushtan.httpd.NehushtanHTTPRequestHandler import NehushtanHTTPRequestHandler


class NehushtanHTTPRequestFilter:
    """
    Since 0.4.0
    """

    def __init__(self, http_handler: NehushtanHTTPRequestHandler, extra_data_dict: dict = None):
        self.__http_handler = http_handler

        # When the request should be deny
        self.http_code_for_denial: int = 200
        self.message_for_denial: str = ''

        # When the request should be accept, something computed would be given out in the dict form
        self.extra_data_dict = extra_data_dict if extra_data_dict is not None else {}

    def get_http_handler(self):
        return self.__http_handler

    @abstractmethod
    def should_accept_request(self) -> bool:
        pass
