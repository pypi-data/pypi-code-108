# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.sig_algo import ScanSigAlgs
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary

sig_algs = [
    "DSA_SHA256",
    "DSA_SHA1",
]


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_supported_groups_openssl1_0_2_DSA"
    sp_out_yaml = "profile_sig_algos_openssl1_0_2_DSA"
    recorder_yaml = "recorder_sig_algos_openssl1_0_2_DSA"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-dsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def check_profile(self, profile):
        assert "signature_algorithms" not in profile["versions"][1]  # SSL30
        assert "signature_algorithms" not in profile["versions"][2]  # TLS10
        assert "signature_algorithms" not in profile["versions"][3]  # TLS11
        prof = profile["versions"][4]  # TLS12
        for a, b in zip(sig_algs, prof["signature_algorithms"]["algorithms"]):
            assert a == b["name"]

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanSigAlgs(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
