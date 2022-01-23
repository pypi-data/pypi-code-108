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
    """

    path = pathlib.Path(__file__)

    cipher_suite = tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_128_CBC_SHA
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    version = tls.Version.TLS11


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
