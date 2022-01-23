# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.eval_cipher_suites import ScanCipherSuites
from tlsmate.workers.supported_groups import ScanSupportedGroups
from tlsmate.workers.sig_algo import ScanSigAlgs
from tlsmate.tlssuite import TlsSuiteTester, TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_out_yaml = "profile_basic_wolfssl3_12_0"
    recorder_yaml = "recorder_basic_profile_wolfssl3_12_0"
    path = pathlib.Path(__file__)
    server_cmd = "utils/start_wolfssl --version {library} --port {server_port}"
    library = TlsLibrary.wolfssl3_12_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        for vers in ["sslv2", "sslv3", "tls10", "tls11", "tls12", "tls13"]:
            tlsmate.config.set(vers, True)
        ScanCipherSuites(tlsmate).run()
        ScanSupportedGroups(tlsmate).run()
        ScanSigAlgs(tlsmate).run()


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
