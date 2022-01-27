# Copyright 2021 Cegal AS
# All rights reserved

from socketserver import TCPServer, ThreadingMixIn


class _ThreadedTCPServer(ThreadingMixIn, TCPServer):
    auth_code = None
    state = None
    nonce = None
    scopes = None

    def __init__(
        self, server_address, handler_class, page_handler, token_client
    ) -> None:
        self.page_handler = page_handler
        self.timeout = 60
        self.token_client = token_client
        super().__init__(server_address, handler_class)

    def handle_timeout(self) -> None:
        return super().handle_timeout()
