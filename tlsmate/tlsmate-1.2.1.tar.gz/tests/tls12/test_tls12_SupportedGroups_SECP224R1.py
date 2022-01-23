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

    name = "SupportedGroups_SECP224R1"
    path = pathlib.Path(__file__)

    cipher_suite = tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL -curves "
        "sect233k1:sect163r2:sect163k1:sect233r1:sect283k1:sect283r1:sect409k1:"
        "sect409r1:sect571k1:sect571r1:secp224r1:secp256k1:brainpoolP256r1:"
        "brainpoolP384r1:brainpoolP512r1"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    supported_groups = [tls.SupportedGroups.SECP224R1]


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
