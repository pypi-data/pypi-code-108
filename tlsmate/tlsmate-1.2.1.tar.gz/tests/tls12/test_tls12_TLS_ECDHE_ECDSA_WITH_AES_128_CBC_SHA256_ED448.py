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
    name = "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256_ED448"

    cipher_suite = tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-ed448 "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    signature_algorithms = [
        tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
        tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
        tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
        tls.SignatureScheme.RSA_PKCS1_SHA256,
        tls.SignatureScheme.RSA_PKCS1_SHA384,
        tls.SignatureScheme.RSA_PKCS1_SHA512,
        tls.SignatureScheme.ECDSA_SHA1,
        tls.SignatureScheme.RSA_PKCS1_SHA1,
        tls.SignatureScheme.ED25519,
        tls.SignatureScheme.ED448,
    ]
    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
