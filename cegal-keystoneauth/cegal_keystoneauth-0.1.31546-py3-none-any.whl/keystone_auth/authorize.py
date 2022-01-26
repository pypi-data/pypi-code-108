# Copyright 2021 Cegal AS
# All rights reserved

from http.server import BaseHTTPRequestHandler
from threading import Thread
from time import sleep
from urllib.parse import parse_qs, urlparse

from cegal.keystone_auth import logger
from cegal.keystone_auth.listener import _ThreadedTCPServer
from cegal.keystone_auth.nonce import _Nonce
from cegal.keystone_auth.pkce import _Pkce
from cegal.keystone_auth.state import _State
from cegal.keystone_auth.responses import DefaultPageHandler


class _AuthorizationClient:
    def __init__(self, page_handler, token_client, context) -> None:
        self._context = context
        self.oidc_client = token_client
        self.page_handler = page_handler
        self.pkce_data = _Pkce()
        self.nonce = _Nonce()
        self.state = _State(self.pkce_data.code_verifier, "http://localhost")
        logger.debug(f"_AuthorizationClient __init__ {self.page_handler}")

    def authorize(self, client_id, requested_scopes, authorize_endpoint):
        self._start_listener()
        params = {
            "response_type": "code",
            "nonce": self.nonce.nonce,
            "state": self.state.state_enc_hashed,  # TODO: proper state
            "code_challenge": self.pkce_data.code_challenge,
            "code_challenge_method": "S256",
            "client_id": client_id,
            "scope": requested_scopes,
            "redirect_uri": f"http://127.0.0.1:{self.port}",
        }

        self._context.request_authcode_url(authorize_endpoint, params)

        attempts = 0
        while self.server.auth_code == None:
            if attempts > 300:
                raise Exception("Time out waiting for login")
            logger.debug("Waiting for login to complete..")
            attempts += 1
            sleep(1)

        self.auth_code = self.server.auth_code

        return (
            self.auth_code,
            self.pkce_data.code_verifier,
            f"http://127.0.0.1:{self.port}",
            self.nonce,
        )

    def _halt_listener(self):
        import time

        try:
            start = time.time()
            while time.time() - start < 300 and not self.server.request_shutdown:
                time.sleep(1)
            self.server.shutdown()
            logger.debug("Server shutdown.")
        except Exception as e:
            logger.error(f"Shutdown thread error {e}")

    def _start_listener(self):
        assert self.page_handler is not None

        self.server = _ThreadedTCPServer(
            ("localhost", 0),
            _AuthorizationRequestHandler,
            self.page_handler,
            self.oidc_client,
        )

        assert self.server.page_handler is not None

        # stopper thread monitors off-thread requests to shutdown the local auth server
        self.server.request_shutdown = False
        self.stopper_thread = Thread(target=self._halt_listener)
        self.stopper_thread.start()

        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.port = self.server.socket.getsockname()[1]
        logger.info("Starting listener on port: " + str(self.port))

    def stop_listener(self):
        logger.debug("stop_listener")
        self.stop_thread = True
        self.server_thread.join()


class _AuthorizationRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args) -> None:
        msg = format % args
        msg = "_AuthorizationRequestHandler: " + msg
        logger.debug(msg)

    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            logger.debug(f"parsed_url {parsed_url}")
            query = parse_qs(parsed_url.query)

            if parsed_url.path == "/":
                # this is the backchannel for the auth_code:
                # the client waits for this to be set before proceeding
                self.server.auth_code = query["code"][0]

                assert self.server.page_handler is not None
                self.server.page_handler.landing_page()
                continue_serving, html = self.server.page_handler.landing_page()
                self.send_response(200)

                # TODO: would be nice to remove the code etc from the url somehow
                self.send_header("Location", self.path.split("?")[0])
                self.end_headers()

                if not continue_serving:
                    self.server.request_shutdown = True

                self.wfile.write(html.encode())
            else:
                logger.debug(f"path: {parsed_url.path}")
                # access_token must be passed lazily since it will not be known
                # until the client derives it fromn the auth_code in the URL in the first page.
                # It must also be thread-safe
                access_token_factory = lambda: self.server.token_client.access_token
                (continue_serving, html) = self.server.page_handler.get(
                    parsed_url, access_token_factory
                )
                self.send_response(200)
                self.end_headers()
                self.wfile.write(html.encode())

                if not continue_serving:
                    self.server.request_shutdown = True
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(ex).encode("UTF-8"))
            self.server.request_shutdown = True
