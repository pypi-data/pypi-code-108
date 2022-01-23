# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.sig_algo import ScanSigAlgs
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary

sig_algs_tls12 = [
    "RSA_PKCS1_SHA256",
    "RSA_PKCS1_SHA384",
    "RSA_PKCS1_SHA512",
    "RSA_PKCS1_SHA224",
    "ECDSA_SECP256R1_SHA256",
    "ECDSA_SECP384R1_SHA384",
    "ECDSA_SECP521R1_SHA512",
    "ECDSA_SECP224R1_SHA224",
]

sig_algs_tls13 = [
    "ECDSA_SECP384R1_SHA384",
    "RSA_PSS_RSAE_SHA256",
    "RSA_PSS_RSAE_SHA384",
    "RSA_PSS_RSAE_SHA512",
]


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_supported_groups_openssl3_0_0"
    sp_out_yaml = "profile_sig_algos_openssl3_0_0"
    recorder_yaml = "recorder_sig_algos_openssl3_0_0"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def check_tls12(self, prof):
        assert len(prof["algorithms"]) == len(sig_algs_tls12)
        for a, b in zip(sig_algs_tls12, prof["algorithms"]):
            assert a == b["name"]

    def check_tls13(self, prof):
        assert len(prof["algorithms"]) == len(sig_algs_tls13)
        for a, b in zip(sig_algs_tls13, prof["algorithms"]):
            assert a == b["name"]

    def check_profile(self, profile):
        self.check_tls12(profile["versions"][4]["signature_algorithms"])
        self.check_tls13(profile["versions"][5]["signature_algorithms"])

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        client = tlsmate.client
        client.init_profile()
        ScanSigAlgs(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
