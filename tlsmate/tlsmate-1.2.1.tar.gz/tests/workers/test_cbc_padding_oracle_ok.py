# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.padding_oracle import ScanPaddingOracle
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl1_0_2"
    recorder_yaml = "recorder_cbc_padding_oracle_ok"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa -- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        self.config.set("oracle_accuracy", "low")
        ScanPaddingOracle(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["vulnerabilities"]["lucky_minus_20"] == "FALSE"
        assert profile["vulnerabilities"]["poodle"] == "TRUE"
        assert profile["vulnerabilities"]["tls_poodle"] == "FALSE"
        cbc = profile["vulnerabilities"]["cbc_padding_oracle"]
        assert cbc["accuracy"] == "LOW"
        assert cbc["vulnerable"] == "FALSE"
        assert len(cbc["oracles"]) == 0


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
