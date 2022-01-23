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

    For more information refer to the documentation of the TcRecorder class.
    """

    path = pathlib.Path(__file__)
    name = "ServerHello"
    # cipher_suite = tls.CipherSuite.TLS_DH_ANON_WITH_AES_128_CBC_SHA
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--no-cert-chain -- -www -ssl2"
    )
    library = TlsLibrary.openssl1_0_2

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS10

    def run(self, tlsmate, is_replaying=False):

        client = tlsmate.client
        end_of_tc_reached = False
        with client.create_connection() as conn:
            ssl_client_hello = msg.SSL2ClientHello()
            ssl_client_hello.cipher_specs = [
                tls.SSLCipherKind.SSL_CK_RC4_128_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_RC4_128_EXPORT40_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_RC2_128_CBC_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_RC2_128_CBC_EXPORT40_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_IDEA_128_CBC_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_DES_64_CBC_WITH_MD5,
                tls.SSLCipherKind.SSL_CK_DES_192_EDE3_CBC_WITH_MD5,
            ]

            conn.send(msg.SSL2ClientHello)
            conn.wait(msg.SSL2ServerHello)
            end_of_tc_reached = True

        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
