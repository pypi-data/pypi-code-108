# -*- coding: utf-8 -*-
"""Implements a class to test the master secret worker.
"""
import pathlib
from tlsmate.workers.master_secret import ScanExtendedMasterSecret
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl1_0_2"
    recorder_yaml = "recorder_master_secret"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_1_1

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanExtendedMasterSecret(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["features"]["extended_master_secret"] == "TRUE"


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
