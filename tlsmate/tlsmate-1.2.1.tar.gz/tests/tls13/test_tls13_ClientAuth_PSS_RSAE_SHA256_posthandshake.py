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

    path = pathlib.Path(__file__)
    name = "ClientAuth_PSS_RSAE_SHA256_posthandshake"
    cipher_suite = tls.CipherSuite.TLS_AES_128_GCM_SHA256
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -cipher ALL -client_sigalgs rsa_pss_rsae_sha256 -legacy_renegotiation"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    version = tls.Version.TLS13

    def run(self, tlsmate, is_replaying=False):
        """The basic scenario to be recorded or replayed.
        """
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [self.version]
        client.profile.cipher_suites = [self.cipher_suite]
        client.profile.supported_groups = self.supported_groups
        client.profile.key_shares = self.supported_groups
        client.profile.signature_algorithms = self.signature_algorithms

        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()

            self.server_input("c\n", timeout=200)

            conn.wait(msg.CertificateRequest, timeout=15000)
            conn.send(msg.Certificate)
            conn.send(msg.CertificateVerify)
            conn.send(msg.Finished)

            conn.timeout(500)
            end_of_tc_reached = True
        assert end_of_tc_reached is True
        assert conn.handshake_completed is True
        return conn


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
