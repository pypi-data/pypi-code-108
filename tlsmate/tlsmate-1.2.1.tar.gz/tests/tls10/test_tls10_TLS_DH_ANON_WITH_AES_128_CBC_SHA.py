# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
import tests.cipher_suite_tester as tester
import tlsmate.tls as tls
import tlsmate.tlssuite as tlssuite


class TestCase(tester.CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.
    """

    path = pathlib.Path(__file__)

    cipher_suite = tls.CipherSuite.TLS_DH_ANON_WITH_AES_128_CBC_SHA
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa -- -www -cipher ALL"
    )
    library = tlssuite.TlsLibrary.openssl1_0_2

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    version = tls.Version.TLS10


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
