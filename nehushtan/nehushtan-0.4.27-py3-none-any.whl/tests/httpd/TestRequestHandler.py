import socketserver
from typing import Tuple, Sequence, Union

from nehushtan.MessageQueue.implement.NehushtanMemoryMessageQueue import NehushtanMemoryMessageQueue
from nehushtan.httpd.NehushtanHTTPRequestHandler import NehushtanHTTPRequestHandler
from nehushtan.httpd.NehushtanHTTPRouter import NehushtanHTTPRouter


class TestRequestHandler(NehushtanHTTPRequestHandler):
    router = NehushtanHTTPRouter()
    mq = NehushtanMemoryMessageQueue()

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        # self.prepare_router()
        super().__init__(request, client_address, server)

    def seek_route_for_process_chains(self, method: str, path: str) \
            -> Tuple[Sequence[Union[type, str]], Tuple[Union[type, str], str]]:
        route = TestRequestHandler.router.check_request_for_route(method, path)
        # self.log_message(route.path_template)
        self.matched_arguments = route.matched_arguments
        self.matched_keyed_arguments = route.matched_keyed_arguments
        return route.get_filter_list(), route.get_controller_target()
