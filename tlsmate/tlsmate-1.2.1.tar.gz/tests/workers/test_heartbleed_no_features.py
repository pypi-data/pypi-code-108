# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.heartbleed import ScanHeartbleed
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestHeartbleedNoFeatures(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl1_0_2"
    recorder_yaml = "recorder_heartbleed_no_features"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa --no-cert-chain "
        "--ca-file ca-certificates "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_1e

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanHeartbleed(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["vulnerabilities"]["heartbleed"] == "UNDETERMINED"


if __name__ == "__main__":
    TestHeartbleedNoFeatures().entry(is_replaying=False)
