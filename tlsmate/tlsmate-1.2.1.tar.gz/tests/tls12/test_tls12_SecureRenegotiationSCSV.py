# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
import logging
from tests.cipher_suite_tester import CipherSuiteTester
from tlsmate import tls
from tlsmate import msg
from tlsmate.tlssuite import TlsLibrary


class TestCase(CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.
    """

    name = "SecureRenegotiationSCSV"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client

        client.set_profile(tls.Profile.LEGACY)
        client.profile.support_scsv_renegotiation = True
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()
            conn.timeout(100)
            conn.handshake()
            conn.timeout(100)
            conn.handshake()
            conn.timeout(100)
            conn.send(msg.AppData(b"GET / HTTP/1.1\n"))
            app_data = conn.wait(msg.AppData)
            while not len(app_data.data):
                app_data = conn.wait(msg.AppData)

            for line in app_data.data.decode("utf-8").split("\n"):
                if line.startswith("s_server"):
                    logging.debug("openssl_command: " + line)
                    conn.recorder.trace(openssl_command=line)
            end_of_tc_reached = True

        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
