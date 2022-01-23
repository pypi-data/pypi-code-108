# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tests.cipher_suite_tester import CipherSuiteTester
from tlsmate import tls
from tlsmate.tlssuite import TlsLibrary


class TestCase(CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.

    Note: The openssl server must be started with "-early_data" and we cannot use
    this option in combination with "-www".
    """

    name = "HelloRetryRequest_handshake"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client
        client.set_profile(tls.Profile.TLS13)
        client.profile.key_shares = []
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()
            end_of_tc_reached = True

        assert end_of_tc_reached is True
        assert conn.msg.hello_retry_request is not None


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
