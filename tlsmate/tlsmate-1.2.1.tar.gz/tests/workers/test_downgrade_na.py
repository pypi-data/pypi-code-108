# -*- coding: utf-8 -*-
"""Implements a class to test the downgrade worker.
"""
import pathlib
from tlsmate.workers.downgrade import ScanDowngrade
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_wolfssl3_12_0"
    recorder_yaml = "recorder_downgrade_na"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_wolfssl --version {library} --port {server_port} "
        "-- -c ../../ca/chains/server-rsa-full.chn -k ../../ca/private/server-rsa.key "
    )
    library = TlsLibrary.wolfssl3_12_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanDowngrade(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["features"]["downgrade_attack_prevention"] == "NA"


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
