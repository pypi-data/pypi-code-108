# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.sig_algo import ScanSigAlgs
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary

sig_algs = ["ED25519", "ED448"]

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

    sp_in_yaml = "profile_supported_groups_openssl3_0_0_ed25519_ed448"
    sp_out_yaml = "profile_sig_algos_openssl3_0_0_ed25519_ed448"
    recorder_yaml = "recorder_sig_algos_openssl3_0_0_ed25519_ed448"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-ed448 --cert2 server-ed25519 "
        "-- -www"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def check_sig_algo(self, prof):
        assert len(prof["algorithms"]) == len(sig_algs)
        for a, b in zip(sig_algs, prof["algorithms"]):
            assert a == b["name"]

    def check_profile(self, profile):
        self.check_sig_algo(profile["versions"][4]["signature_algorithms"])
        self.check_sig_algo(profile["versions"][5]["signature_algorithms"])

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        client = tlsmate.client
        client.init_profile()
        ScanSigAlgs(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
