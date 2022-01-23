# -*- coding: utf-8 -*-
"""Implements a class to test the grease worker.
"""
import pathlib
from tlsmate.workers.grease import ScanGrease
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_resumption_openssl3_0_0"
    recorder_yaml = "recorder_grease"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanGrease(tlsmate).run()
        profile = server_profile.make_serializable()
        grease_prof = profile["features"]["grease"]
        for param in (
            "version_tolerance",
            "cipher_suite_tolerance",
            "extension_tolerance",
            "group_tolerance",
            "sig_algo_tolerance",
            "psk_mode_tolerance",
        ):
            assert grease_prof[param] == "TRUE"


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
