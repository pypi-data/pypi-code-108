# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.supported_groups import ScanSupportedGroups
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_openssl1_0_2"
    sp_out_yaml = "profile_supported_groups_openssl1_0_2"
    recorder_yaml = "recorder_supported_groups_openssl1_0_2"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def check_ssl30(self, profile):
        assert profile["extension_supported"] == "FALSE"
        assert len(profile["groups"]) == 1
        assert profile["groups"][0]["name"] == "SECP256R1"

    def check_tls(self, profile):
        assert profile["extension_supported"] == "TRUE"
        assert profile["server_preference"] == "NA"
        assert profile["groups_advertised"] == "NA"
        assert len(profile["groups"]) == 1
        assert profile["groups"][0]["name"] == "SECP256R1"

    def check_profile(self, profile):
        self.check_ssl30(profile["versions"][1]["supported_groups"])
        self.check_tls(profile["versions"][2]["supported_groups"])
        self.check_tls(profile["versions"][3]["supported_groups"])
        self.check_tls(profile["versions"][4]["supported_groups"])

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanSupportedGroups(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
