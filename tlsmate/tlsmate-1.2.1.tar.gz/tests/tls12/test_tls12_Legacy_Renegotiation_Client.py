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

    name = "Legacy_Renegotiation_Client"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL -legacy_renegotiation"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [tls.Version.TLS12]
        client.profile.cipher_suites = [
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        ]
        client.profile.supported_groups = [
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
        ]
        client.profile.signature_algorithms = [tls.SignatureScheme.RSA_PKCS1_SHA256]
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()
            conn.handshake()
            conn.send(msg.AppData(b"GET / HTTP/1.1\n"))
            while True:
                app_data = conn.wait(msg.AppData)
                if len(app_data.data):
                    break
            for line in app_data.data.decode("utf-8").split("\n"):
                if line.startswith("s_server"):
                    logging.debug("openssl_command: " + line)
            end_of_tc_reached = True
        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
