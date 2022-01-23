# -*- coding: utf-8 -*-
"""Implements a class to test the ocsp-stapling worker.
"""
import pathlib
from tlsmate.workers.ocsp_stapling import ScanOcspStapling
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_wolfssl3_12_0"
    recorder_yaml = "recorder_ocsp_multi_stapling_ok"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_wolfssl --version {library} --port {server_port} "
        "-- -c ../../ca/chains/server-rsa-full.chn -k ../../ca/private/server-rsa.key "
        "-o"
    )

    library = TlsLibrary.wolfssl4_8_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanOcspStapling(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["features"]["ocsp_stapling"] == "TRUE"
        assert profile["features"]["ocsp_multi_stapling"] == "TRUE"


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
