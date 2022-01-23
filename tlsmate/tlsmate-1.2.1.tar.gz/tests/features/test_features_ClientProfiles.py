# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tests.cipher_suite_tester import CipherSuiteTester
from tlsmate import tls
from tlsmate import msg
from tlsmate.tlssuite import TlsLibrary


class TestCase(CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.
    """

    name = "ClientProfiles"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa -- -www"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client

        client.set_profile(tls.Profile.LEGACY)
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            end_of_tc_reached = True
        assert end_of_tc_reached is True

        client.set_profile(tls.Profile.INTEROPERABILITY)
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            end_of_tc_reached = True
        assert end_of_tc_reached is True

        client.set_profile(tls.Profile.MODERN)
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            end_of_tc_reached = True
        assert end_of_tc_reached is True

        client.set_profile(tls.Profile.TLS13)
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            end_of_tc_reached = True
        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
